"""Entry point for ARC-AGI LLM evaluation pipeline."""

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from arc.eval.config import load_config, _DATA_DIR_TEMPLATE
from arc.eval.db import ResultDB
from arc.eval.llm import call_llm
from arc.eval.prompt import build_messages
from arc.eval.test import extract_code, run_tests


def load_tasks(data_dir: str) -> dict[str, dict]:
    """Load all ARC tasks from a directory of JSON files.

    Returns: {task_id: {"train": [...], "test": [...]}}
    """
    tasks = {}
    for path in sorted(Path(data_dir).glob("*.json")):
        with open(path) as f:
            tasks[path.stem] = json.load(f)
    return tasks


def evaluate_single_task(task_id, task_data, client, cfg, db, run_name):
    """Evaluate a single ARC task: prompt -> LLM -> test -> DB."""
    start = time.time()
    mode = cfg["eval"]["mode"]
    endpoint_name = cfg["endpoint"]["name"]

    base_result = {
        "run_name": run_name,
        "task_id": task_id,
        "mode": mode,
        "endpoint_name": endpoint_name,
    }

    try:
        messages = build_messages(task_data["train"], [tc["input"] for tc in task_data["test"]])
        llm_result = call_llm(client, cfg, messages)

        base_result.update({
            "raw_response": llm_result.text,
            "token_usage": json.dumps(llm_result.usage),
            "tool_rounds": llm_result.tool_rounds,
            "duration_s": time.time() - start,
        })

        code = extract_code(llm_result.text)
        if code is None:
            base_result.update({
                "status": "error_extract",
                "extracted_code": None,
                "test_passed": 0, "test_total": len(task_data["test"]),
                "correct": 0,
                "error_message": "No test_transform function found in LLM output",
            })
            db.save_result(base_result)
            return base_result

        test_result = run_tests(code, task_data["test"], cfg["python_path"])

        base_result.update({
            "status": test_result["status"],
            "extracted_code": code,
            "test_passed": test_result["passed"],
            "test_total": test_result["total"],
            "correct": 1 if test_result["correct"] else 0,
            "error_message": None,
        })
        db.save_result(base_result)
        return base_result

    except Exception as e:
        base_result.update({
            "status": "error_llm",
            "raw_response": base_result.get("raw_response"),
            "extracted_code": None,
            "test_passed": 0, "test_total": 0,
            "correct": 0,
            "token_usage": base_result.get("token_usage"),
            "tool_rounds": base_result.get("tool_rounds", 0),
            "duration_s": time.time() - start,
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

    done = db.get_completed_task_ids(run_name)
    remaining = {tid: td for tid, td in tasks.items() if tid not in done}

    print(f"Run: {run_name} | Mode: {mode} | Tasks: {len(remaining)}/{len(tasks)} remaining")

    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(evaluate_single_task, tid, td, client, cfg, db, run_name): tid
            for tid, td in remaining.items()
        }
        for future in as_completed(futures):
            tid = futures[future]
            result = future.result()
            completed += 1
            status = result["status"]
            print(f"[{completed}/{len(remaining)}] {tid}: {status}")

    summary = db.get_run_summary(run_name)
    print(f"\nDone. Accuracy: {summary['correct']}/{summary['total']} ({summary['accuracy']:.1%})")


if __name__ == "__main__":
    main()
