"""CLI entry point for ARC evaluation pipeline."""

import argparse
import time
from datetime import datetime
from pathlib import Path

from .config import (
    DATASET_PATHS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
)
from .prompt import build_initial_messages, append_retry
from .llm_client import call_llm
from .code_extract import extract_code
from .safe_exec import execute_transform
from .evaluate import compare_grids, verify_on_train, format_wrong_output_msg
from .db import ResultDB


def load_tasks(data_dir: str) -> dict[str, dict]:
    """Load all task JSON files from a directory, sorted by name."""
    import json
    tasks = {}
    data_path = Path(data_dir)
    for f in sorted(data_path.glob("*.json")):
        with open(f) as fp:
            tasks[f.stem] = json.load(fp)
    return tasks


def evaluate_task(
    task_id: str,
    task_data: dict,
    max_retries: int,
    timeout: int,
    temperature: float,
    db: ResultDB,
    run_id: str,
) -> dict:
    """Evaluate a single ARC task. Logs every attempt to SQLite immediately."""
    train_examples = task_data["train"]
    test_cases = task_data["test"]
    start_time = time.time()

    all_solved = True
    passed_count = 0
    last_code = None

    for test_idx, test_case in enumerate(test_cases):
        test_input = test_case["input"]
        test_output = test_case["output"]
        print(f"  Test case {test_idx + 1}/{len(test_cases)}")

        def _log(attempt, **kwargs):
            db.insert_attempt(run_id, task_id, test_idx, attempt, **kwargs)

        # Build initial conversation
        messages = build_initial_messages(train_examples, test_input)
        solved = False

        for attempt in range(1, max_retries + 1):
            # Call LLM
            num_msgs = len([m for m in messages if m["role"] != "system"])
            print(f"    [{attempt}/{max_retries}] Calling LLM ({num_msgs} messages in context)...", flush=True)
            t0 = time.time()
            try:
                response = call_llm(messages, temperature=temperature)
            except RuntimeError as e:
                _log(attempt, error_type="api_error", error_msg=str(e))
                print(f"    [{attempt}/{max_retries}] API error ({time.time()-t0:.0f}s): {e}")
                break
            llm_time = time.time() - t0
            resp_len = len(response)
            print(f"    [{attempt}/{max_retries}] LLM responded ({llm_time:.0f}s, {resp_len} chars)")

            # Extract code
            code = extract_code(response)
            if code is None:
                error_msg = (
                    "Could not extract a valid Python function from your response. "
                    "Please write a `def transform(input_grid)` function inside a "
                    "```python code block."
                )
                _log(attempt, llm_response=response,
                     error_type="extraction_failed", error_msg=error_msg)
                messages = append_retry(messages, response, error_msg)
                print(f"    [{attempt}/{max_retries}] FAIL: code extraction failed")
                continue

            last_code = code

            # Verify on training examples
            train_result = verify_on_train(
                code, train_examples, execute_transform, timeout
            )

            if not train_result["passed"]:
                error_msg = train_result["error_msg"]
                _log(attempt, llm_response=response, extracted_code=code,
                     train_pass=False, error_type="train_fail", error_msg=error_msg)
                messages = append_retry(messages, response, error_msg)
                print(f"    [{attempt}/{max_retries}] FAIL: train verification failed")
                continue

            # Run on test input
            test_result = execute_transform(code, test_input, timeout=timeout)
            if not test_result["success"]:
                error_msg = f"Error on test input:\n{test_result['error']}"
                _log(attempt, llm_response=response, extracted_code=code,
                     train_pass=True, error_type="test_exec_error", error_msg=error_msg)
                messages = append_retry(messages, response, error_msg)
                print(f"    [{attempt}/{max_retries}] FAIL: test execution error")
                continue

            # Compare with expected
            cmp = compare_grids(test_result["output"], test_output)

            if cmp["correct"]:
                solved = True
                _log(attempt, llm_response=response, extracted_code=code,
                     train_pass=True, test_correct=True, cell_accuracy=1.0)
                print(f"    [{attempt}/{max_retries}] SOLVED!")
                break
            else:
                error_msg = format_wrong_output_msg(
                    "test input", test_output, test_result["output"], cmp
                )
                _log(attempt, llm_response=response, extracted_code=code,
                     train_pass=True, test_correct=False,
                     cell_accuracy=cmp["cell_accuracy"],
                     error_type="wrong_output", error_msg=error_msg)
                messages = append_retry(messages, response, error_msg)
                print(f"    [{attempt}/{max_retries}] FAIL: wrong output (cell acc: {cmp['cell_accuracy']:.1%})")

        if solved:
            passed_count += 1
        else:
            all_solved = False

    elapsed = time.time() - start_time

    # Write task-level result
    db.upsert_task(
        run_id, task_id,
        solved=all_solved,
        num_test_cases=len(test_cases),
        test_cases_passed=passed_count,
        total_time_seconds=round(elapsed, 2),
        final_code=last_code,
    )

    return {
        "solved": all_solved,
        "test_cases_passed": passed_count,
        "num_test_cases": len(test_cases),
        "total_time_seconds": round(elapsed, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="ARC-AGI LLM Evaluation Pipeline")
    parser.add_argument(
        "--dataset", choices=["arc1", "arc2"], default="arc1",
        help="Dataset to evaluate (default: arc1)",
    )
    parser.add_argument(
        "--split", choices=["training", "evaluation"], default="training",
        help="Data split (default: training)",
    )
    parser.add_argument(
        "--task-id", type=str, default=None,
        help="Run a single task by ID",
    )
    parser.add_argument(
        "--max-tasks", type=int, default=None,
        help="Max number of tasks to evaluate",
    )
    parser.add_argument(
        "--max-retries", type=int, default=DEFAULT_MAX_RETRIES,
        help=f"Max retry attempts per test case (default: {DEFAULT_MAX_RETRIES})",
    )
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT,
        help=f"Code execution timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--temperature", type=float, default=DEFAULT_TEMPERATURE,
        help=f"LLM temperature (default: {DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "--run-name", type=str, default=None,
        help="Name for this run (default: timestamp). Reusing a name resumes.",
    )
    args = parser.parse_args()

    # Resolve paths
    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = project_root / DATASET_PATHS[args.dataset][args.split]

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Run: git clone --depth 1 https://github.com/fchollet/ARC-AGI.git")
        print("     git clone --depth 1 https://github.com/arcprize/ARC-AGI-2.git")
        return

    # Load tasks
    tasks = load_tasks(str(data_dir))
    if args.task_id:
        if args.task_id not in tasks:
            print(f"Error: Task '{args.task_id}' not found in {data_dir}")
            return
        tasks = {args.task_id: tasks[args.task_id]}
    if args.max_tasks:
        task_ids = list(tasks.keys())[: args.max_tasks]
        tasks = {tid: tasks[tid] for tid in task_ids}

    # Setup DB
    run_name = args.run_name or datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = project_root / "results" / run_name
    results_dir.mkdir(parents=True, exist_ok=True)
    db_path = results_dir / "results.db"
    db = ResultDB(db_path)
    db.insert_run(run_name, args.dataset, args.split,
                  args.max_retries, args.timeout, args.temperature)

    # Skip already-completed tasks (resume support)
    done = db.get_completed_task_ids(run_name)
    remaining = {tid: td for tid, td in tasks.items() if tid not in done}

    print(f"=== ARC-AGI Evaluation ===")
    print(f"Dataset:     {args.dataset} / {args.split}")
    print(f"Total tasks: {len(tasks)}")
    if done:
        print(f"Resuming:    {len(done)} already done, {len(remaining)} remaining")
    print(f"Max retries: {args.max_retries}")
    print(f"Timeout:     {args.timeout}s")
    print(f"Temperature: {args.temperature}")
    print(f"Results DB:  {db_path}")
    print()

    # Evaluate
    solved_so_far = 0
    total_so_far = 0
    for i, (task_id, task_data) in enumerate(remaining.items(), 1):
        n_test = len(task_data["test"])
        n_train = len(task_data["train"])
        print(f"[{i}/{len(remaining)}] Task: {task_id} ({n_train} train, {n_test} test)")
        result = evaluate_task(
            task_id, task_data, args.max_retries, args.timeout,
            args.temperature, db, run_name,
        )
        total_so_far += 1
        if result["solved"]:
            solved_so_far += 1
        status = "SOLVED" if result["solved"] else "FAILED"
        print(
            f"  {status} ({result['test_cases_passed']}/{result['num_test_cases']} "
            f"test cases, {result['total_time_seconds']:.1f}s) "
            f"| Running: {solved_so_far}/{total_so_far} solved ({solved_so_far/total_so_far:.0%})\n"
        )

    # Print summary
    summary = db.get_summary(run_name)
    print(f"=== Summary ===")
    print(f"Tasks evaluated: {summary['tasks_evaluated']}")
    print(f"Tasks solved:    {summary['tasks_solved']} ({summary['solve_rate']:.1%})")
    print(f"Test cases:      {summary['test_cases_passed']}/{summary['total_test_cases']}")
    print(f"Results DB:      {db_path}")

    db.close()


if __name__ == "__main__":
    main()
