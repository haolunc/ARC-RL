"""Entry point for ARC-AGI LLM evaluation pipeline."""

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from arc.eval.config import load_config, _DATA_DIR_TEMPLATE
from arc.eval.db import ResultDB, LogDB
from arc.eval.llm import call_llm
from arc.eval.prompt import build_messages
from arc.eval.test import run_tests


def load_tasks(data_dir: str) -> dict[str, dict]:
    """Load all ARC tasks from a directory of JSON files.

    Returns: {task_id: {"train": [...], "test": [...]}}
    """
    tasks = {}
    for path in sorted(Path(data_dir).glob("*.json")):
        with open(path) as f:
            tasks[path.stem] = json.load(f)
    return tasks


def evaluate_single_task(task_id, task_data, client, cfg, db, log_db):
    """Evaluate a single ARC task: prompt -> LLM -> test -> DB."""
    print(f"[{task_id}] Starting evaluation")
    start = time.time()
    base_result = {"task_id": task_id}
    extracted_code = None

    try:
        messages = build_messages(task_data["train"], [tc["input"] for tc in task_data["test"]])
        llm_result = call_llm(client, cfg, messages, task_id, log_db)
        extracted_code = llm_result.extracted_code

        llm_duration = time.time() - start
        print(f"[{task_id}] LLM complete: {llm_result.tool_rounds} tool rounds, {llm_duration:.1f}s")

        base_result.update({
            "token_usage": json.dumps(llm_result.usage),
            "tool_rounds": llm_result.tool_rounds,
            "duration_s": time.time() - start,
        })

        if llm_result.error:
            print(f"[{task_id}] LLM error: {llm_result.error}")
            base_result.update({
                "status": "error_llm",
                "test_passed": 0, "test_total": 0,
                "correct": 0,
                "extracted_code": extracted_code,
                "error_message": llm_result.error,
            })
            db.save_result(base_result)
            return base_result

        if extracted_code is None:
            print(f"[{task_id}] No test_transform found in output")
            base_result.update({
                "status": "error_extract",
                "test_passed": 0, "test_total": len(task_data["test"]),
                "correct": 0,
                "extracted_code": None,
                "error_message": "No test_transform function found in LLM output",
            })
            db.save_result(base_result)
            return base_result

        print(f"[{task_id}] Running tests...")
        test_result = run_tests(extracted_code, task_data["test"], cfg["python_path"])
        print(f"[{task_id}] Tests: {test_result['passed']}/{test_result['total']}, correct={test_result['correct']}")

        base_result.update({
            "status": test_result["status"],
            "test_passed": test_result["passed"],
            "test_total": test_result["total"],
            "correct": 1 if test_result["correct"] else 0,
            "test_details": json.dumps(test_result["details"]),
            "extracted_code": extracted_code,
            "error_message": None,
        })
        db.save_result(base_result)
        return base_result

    except Exception as e:
        print(f"[{task_id}] Error: {e}")
        base_result.update({
            "status": "error_llm",
            "test_passed": 0, "test_total": 0,
            "correct": 0,
            "token_usage": base_result.get("token_usage"),
            "tool_rounds": base_result.get("tool_rounds", 0),
            "duration_s": time.time() - start,
            "extracted_code": extracted_code,
            "error_message": str(e),
        })
        db.save_result(base_result)
        return base_result


def main():
    parser = argparse.ArgumentParser(description="ARC-AGI LLM Evaluation Pipeline")
    parser.add_argument("config", type=str, help="Path to config YAML file")
    args = parser.parse_args()

    cfg = load_config(args.config)
    project_root = Path(__file__).resolve().parent.parent.parent

    ep = cfg["endpoint"]
    ev = cfg["eval"]
    client = OpenAI(
        base_url=ep["base_url"],
        api_key=ep["api_key"],
        timeout=float(ev.get("llm_timeout", 180)),
    )

    mode = ev["mode"]
    max_workers = ev.get("max_workers", 1)

    split = cfg["data"]["split"]
    max_tasks = cfg["data"].get("max_tasks")
    cfg_task_ids = cfg["data"].get("task_ids")

    data_dir = project_root / _DATA_DIR_TEMPLATE.format(split=split)
    all_tasks = load_tasks(str(data_dir))

    if cfg_task_ids:
        tasks = {tid: all_tasks[tid] for tid in cfg_task_ids}
    elif max_tasks:
        tasks = dict(list(all_tasks.items())[:max_tasks])
    else:
        tasks = all_tasks

    run_name = ev.get("run_name") or datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = project_root / "results" / run_name
    results_dir.mkdir(parents=True, exist_ok=True)
    db = ResultDB(results_dir / "results.db")
    log_db = LogDB(results_dir / "logs.db")

    done = db.get_completed_task_ids()
    remaining = {tid: td for tid, td in tasks.items() if tid not in done}

    print(f"Run: {run_name} | Mode: {mode} | Tasks: {len(remaining)}/{len(tasks)} remaining")

    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(evaluate_single_task, tid, td, client, cfg, db, log_db): tid
            for tid, td in remaining.items()
        }
        for future in as_completed(futures):
            tid = futures[future]
            result = future.result()
            completed += 1
            status = result["status"]
            print(f"[{completed}/{len(remaining)}] {tid}: {status}")

    summary = db.get_run_summary()
    print(f"\nDone. Accuracy: {summary['correct']}/{summary['total']} ({summary['accuracy']:.1%})")


if __name__ == "__main__":
    main()
