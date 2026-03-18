"""CLI entry point for ARC evaluation pipeline."""

import argparse
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from .config import load_config, EXEC_TIMEOUT, MAX_TOOL_CALLS, TEMPERATURE, _DATA_DIR_TEMPLATE
from .prompt import build_messages
from openai import OpenAI
from .llm_client import solve
from .code_extract import extract_code, extract_thinking
from .safe_exec import execute_transform
from .evaluate import compare_grids
from .tools import TOOL_DEFINITION, extract_tool_code, run_python_tool
from .db import ResultDB

_print_lock = threading.Lock()


def _safe_json_dumps(obj):
    """Serialize to JSON, converting non-serializable API objects to dicts."""
    def _default(o):
        # Handle raw API response objects
        if hasattr(o, "model_dump"):
            return o.model_dump()
        if hasattr(o, "__dict__"):
            return {k: v for k, v in o.__dict__.items() if not k.startswith("_")}
        return str(o)
    return json.dumps(obj, ensure_ascii=False, default=_default)


def _tprint(task_id: str, msg: str):
    """Thread-safe print with task ID prefix."""
    with _print_lock:
        print(f"[{task_id[:8]}] {msg}", flush=True)


def load_tasks(data_dir: str) -> dict[str, dict]:
    """Load all task JSON files from a directory, sorted by name."""
    tasks = {}
    data_path = Path(data_dir)
    for f in sorted(data_path.glob("*.json")):
        with open(f) as fp:
            tasks[f.stem] = json.load(fp)
    return tasks


def _log_solve_result(solve_result, db, run_id, task_id):
    """Log all steps from a SolveResult to the database."""
    for step_idx, step in enumerate(solve_result.steps, 1):
        thinking = None
        if step.llm_result.content:
            thinking, _ = extract_thinking(step.llm_result.content)

        llm_call_id = db.insert_llm_call(
            run_id, task_id, 0, step_idx,
            llm_result=step.llm_result,
            input_messages=_safe_json_dumps(step.input_messages),
            thinking=thinking,
        )

        for tc in step.tool_calls:
            db.insert_tool_call(
                llm_call_id, tc.index,
                tool_call_id=tc.call_id,
                tool_name=tc.tool_name,
                tool_arguments=tc.arguments,
                tool_output=tc.output,
                duration_seconds=tc.duration_seconds,
            )


def _make_tool_runner(task_context):
    """Create a tool runner callback for solve()."""
    def run_tool(tool_call):
        code = extract_tool_code(tool_call)
        result = run_python_tool(code, task_context)
        output = result["output"]
        return code, output
    return run_tool


def evaluate_task(
    task_id: str,
    task_data: dict,
    mode: str,
    python_path: str,
    db: ResultDB,
    run_id: str,
    client: OpenAI,
    model: str,
) -> dict:
    """Evaluate a single ARC task. One LLM session, validated against all test cases."""
    train_examples = task_data["train"]
    test_cases = task_data["test"]
    start_time = time.time()
    log = lambda msg: _tprint(task_id, msg)

    test_inputs = [tc["input"] for tc in test_cases]

    # Build prompt with ALL test inputs
    input_msgs = build_messages(mode, train_examples, test_inputs)

    task_context = {
        "train_examples": train_examples,
        "test_inputs": test_inputs,
        "timeout": EXEC_TIMEOUT,
        "python_path": python_path,
    }

    def _fail(code=None):
        total_time = round(time.time() - start_time, 2)
        db.upsert_task(run_id, task_id, mode=mode, solved=False,
                       num_test_cases=len(test_cases), test_cases_passed=0,
                       total_time_seconds=total_time, final_code=code)
        return {"solved": False, "test_cases_passed": 0,
                "num_test_cases": len(test_cases), "total_time_seconds": total_time}

    # Solve with a single LLM session
    try:
        if mode == "sandbox_tools":
            result = solve(
                client, model, TEMPERATURE, input_msgs,
                tools=[TOOL_DEFINITION], max_tool_calls=MAX_TOOL_CALLS,
                run_tool_fn=_make_tool_runner(task_context), log=log)
        else:
            tools = [{"type": "code_interpreter"}] if mode == "native_tools" else None
            result = solve(client, model, TEMPERATURE, input_msgs, tools=tools, log=log)
    except RuntimeError as e:
        log(f"API error: {e}")
        db.insert_llm_call(
            run_id, task_id, 0, 0,
            input_messages=_safe_json_dumps(input_msgs),
            success=False, error_type="api_error", error_msg=str(e))
        return _fail()

    # Log all LLM/tool calls to DB
    _log_solve_result(result, db, run_id, task_id)

    if not result.content:
        log("FAIL: no response text")
        return _fail()

    # Extract ONE test_transform function
    code = extract_code(result.content)
    if code is None:
        log("FAIL: could not extract test_transform function")
        return _fail()

    # Validate against ALL test cases
    all_solved = True
    passed_count = 0
    for test_idx, test_case in enumerate(test_cases):
        test_input = test_case["input"]
        test_output = test_case["output"]
        log(f"Validating test case {test_idx + 1}/{len(test_cases)}")

        test_result = execute_transform(code, test_input, timeout=EXEC_TIMEOUT,
                                        python_path=python_path)
        if not test_result["success"]:
            log(f"FAIL: execution error — {test_result['error'][:100]}")
            all_solved = False
            continue

        cmp = compare_grids(test_result["output"], test_output)
        if cmp["correct"]:
            log("SOLVED!")
            passed_count += 1
        else:
            log(f"FAIL: wrong output (cell acc: {cmp['cell_accuracy']:.1%})")
            all_solved = False

    total_time = round(time.time() - start_time, 2)
    db.upsert_task(run_id, task_id, mode=mode, solved=all_solved,
                   num_test_cases=len(test_cases), test_cases_passed=passed_count,
                   total_time_seconds=total_time, final_code=code)
    return {
        "solved": all_solved,
        "test_cases_passed": passed_count,
        "num_test_cases": len(test_cases),
        "total_time_seconds": total_time,
    }


def main():
    parser = argparse.ArgumentParser(description="ARC-AGI LLM Evaluation Pipeline")
    parser.add_argument("config", type=str, help="Path to config YAML file")
    args = parser.parse_args()

    cfg = load_config(args.config)
    project_root = Path(__file__).resolve().parent.parent.parent

    # Initialize LLM client
    ep = cfg["endpoint"]
    ev = cfg["eval"]
    client = OpenAI(
        base_url=ep["base_url"],
        api_key=ep["api_key"],
        timeout=float(ev["llm_timeout"]),
    )
    model = ep["model"]

    python_path = cfg["python_path"]
    mode = ev["mode"]
    max_workers = ev.get("max_workers", 1)

    split = cfg["data"]["split"]
    max_tasks = cfg["data"].get("max_tasks")
    cfg_task_ids = cfg["data"].get("task_ids")

    # Resolve data directory
    data_dir = project_root / _DATA_DIR_TEMPLATE.format(split=split)
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Run: git clone --depth 1 https://github.com/arcprize/ARC-AGI-2.git")
        return

    all_tasks = load_tasks(str(data_dir))

    # Task selection
    if cfg_task_ids:
        missing = [tid for tid in cfg_task_ids if tid not in all_tasks]
        if missing:
            print(f"Error: Task(s) not found in {data_dir}: {', '.join(missing)}")
            return
        tasks = {tid: all_tasks[tid] for tid in cfg_task_ids}
    elif max_tasks:
        tasks = dict(list(all_tasks.items())[:max_tasks])
    else:
        tasks = all_tasks

    # Determine run name, open/create DB
    run_name = cfg["eval"].get("run_name") or datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = project_root / "results" / run_name
    db_path = results_dir / "results.db"
    results_dir.mkdir(parents=True, exist_ok=True)
    db = ResultDB(db_path)

    # Dedup — skip already completed tasks
    done = db.get_completed_task_ids(run_name)
    remaining = {tid: td for tid, td in tasks.items() if tid not in done}

    print(f"=== ARC-AGI Evaluation ===")
    print(f"Run name:       {run_name}")
    print(f"Mode:           {mode}")
    print(f"Endpoint:       {ep['name']} ({ep['model']})")
    print(f"Split:          {split}")
    print(f"Total tasks:    {len(tasks)}")
    if done:
        print(f"Resuming:       {len(done)} already done, {len(remaining)} remaining")
    print(f"Workers:        {max_workers}")
    print(f"Results DB:     {db_path}")
    print()

    # Evaluate
    solved_counter = {"solved": 0, "total": 0}
    counter_lock = threading.Lock()

    def _run_one(task_id, task_data):
        n_test = len(task_data["test"])
        n_train = len(task_data["train"])
        _tprint(task_id, f"START ({n_train} train, {n_test} test)")
        result = evaluate_task(
            task_id, task_data, mode,
            python_path, db, run_name, client, model,
        )
        with counter_lock:
            solved_counter["total"] += 1
            if result["solved"]:
                solved_counter["solved"] += 1
            s, t = solved_counter["solved"], solved_counter["total"]
        status = "SOLVED" if result["solved"] else "FAILED"
        _tprint(task_id,
            f"{status} ({result['test_cases_passed']}/{result['num_test_cases']} "
            f"test cases, {result['total_time_seconds']:.1f}s) "
            f"| Running: {s}/{t} solved ({s/t:.0%})"
        )
        return result

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_run_one, task_id, task_data): task_id
            for task_id, task_data in remaining.items()
        }
        for future in as_completed(futures):
            task_id = futures[future]
            try:
                future.result()
            except Exception as e:
                _tprint(task_id, f"ERROR: {e}")

    # Print summary
    summary = db.get_summary(run_name)
    print(f"\n=== Summary ===")
    print(f"Tasks evaluated: {summary['tasks_evaluated']}")
    print(f"Tasks solved:    {summary['tasks_solved']} ({summary['solve_rate']:.1%})")
    print(f"Test cases:      {summary['test_cases_passed']}/{summary['total_test_cases']}")
    print(f"LLM calls:       {summary['total_llm_calls']}")
    print(f"Tokens:          {summary['total_input_tokens']} in / {summary['total_output_tokens']} out"
          + (f" ({summary['total_cached_tokens']} cached)" if summary['total_cached_tokens'] else "")
          + (f" ({summary['total_reasoning_tokens']} reasoning)" if summary['total_reasoning_tokens'] else ""))
    print(f"LLM time:        {summary['total_llm_duration_seconds']:.1f}s")
    print(f"Results DB:      {db_path}")

    db.close()


if __name__ == "__main__":
    main()
