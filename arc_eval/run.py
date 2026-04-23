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
    SAFE_MAX_INPUT_TOKENS,
    CHARS_PER_TOKEN_ESTIMATE,
)
from .prompt import build_initial_messages, append_retry, format_grid
from .llm_client import call_llm
from .code_extract import extract_code
from .safe_exec import execute_transform
from .evaluate import compare_grids, verify_on_train
from .db import ResultDB


def load_tasks(data_dir: str) -> dict[str, dict]:
    """Load all task JSON files from a directory, sorted by name."""
    import json

    tasks = {}
    data_path = Path(data_dir)
    for f in sorted(data_path.glob("*.json")):
        with open(f, encoding="utf-8") as fp:
            tasks[f.stem] = json.load(fp)
    return tasks


def approx_token_count(messages: list[dict]) -> int:
    """Approximate token count from message contents using a chars/token heuristic."""
    total_chars = sum(len(m["content"]) for m in messages)
    return total_chars // CHARS_PER_TOKEN_ESTIMATE


def enforce_context_budget(messages: list[dict]) -> list[dict]:
    """Trim conversation history if approximate input tokens exceed safe budget.

    Strategy:
    - keep system prompt
    - keep original task prompt
    - keep only the latest assistant/user retry pair
    """
    approx_tokens = approx_token_count(messages)
    if approx_tokens <= SAFE_MAX_INPUT_TOKENS:
        return messages

    print(
        f"    Warning: prompt too large (~{approx_tokens} tokens). "
        f"Trimming to stay under ~{SAFE_MAX_INPUT_TOKENS} tokens."
    )

    system_msgs = [m for m in messages if m["role"] == "system"]
    non_system = [m for m in messages if m["role"] != "system"]

    if len(non_system) <= 1:
        return messages

    initial_user = non_system[0]
    tail = non_system[-2:] if len(non_system) >= 3 else non_system[1:]
    trimmed = system_msgs + [initial_user] + tail

    trimmed_tokens = approx_token_count(trimmed)
    print(f"    Trimmed context to ~{trimmed_tokens} tokens")

    return trimmed


def evaluate_task(
    task_id: str,
    task_data: dict,
    max_retries: int,
    timeout: int,
    temperature: float,
    db: ResultDB,
    run_id: str,
) -> dict:
    """Evaluate a single ARC task. Logs every attempt to SQLite immediately.

    Important:
    - Retries are allowed for API/extraction/train/test-exec failures.
    - Retries are NOT allowed after checking test correctness, to avoid leaking
      the hidden test output into subsequent prompts.
    """
    train_examples = task_data["train"]
    test_cases = task_data["test"]
    start_time = time.time()

    all_solved = True
    passed_count = 0
    last_code = None

    for test_idx, test_case in enumerate(test_cases):
        test_input = test_case["input"]
        test_output = test_case.get("output")
        if test_output is None:
            raise ValueError(
                f"Task {task_id} test case {test_idx} has no public output."
            )

        print(f"  Test case {test_idx + 1}/{len(test_cases)}")

        messages = build_initial_messages(train_examples, test_input)
        solved = False

        for attempt in range(1, max_retries + 1):
            messages = enforce_context_budget(messages)

            num_msgs = len([m for m in messages if m["role"] != "system"])
            prompt_chars = sum(len(m["content"]) for m in messages)
            prompt_tokens = approx_token_count(messages)

            print(
                f"    [{attempt}/{max_retries}] Calling LLM "
                f"({num_msgs} messages, {prompt_chars} chars, ~{prompt_tokens} tokens in context)...",
                flush=True,
            )

            t0 = time.time()
            try:
                response = call_llm(messages, temperature=temperature)
            except RuntimeError as e:
                db.insert_attempt(
                    run_id=run_id,
                    task_id=task_id,
                    test_index=test_idx,
                    attempt=attempt,
                    prompt_chars=prompt_chars,
                    prompt_tokens=prompt_tokens,
                    llm_response=None,
                    extracted_code=None,
                    train_pass=None,
                    test_correct=None,
                    cell_accuracy=None,
                    error_type="api_error",
                    error_msg=str(e),
                )
                print(
                    f"    [{attempt}/{max_retries}] API error ({time.time() - t0:.0f}s): {e}"
                )
                break

            llm_time = time.time() - t0
            resp_len = len(response)
            print(
                f"    [{attempt}/{max_retries}] LLM responded "
                f"({llm_time:.0f}s, {resp_len} chars)"
            )

            code = extract_code(response)
            if code is None:
                error_msg = (
                    "Could not extract a valid Python function from your response. "
                    "Please write a `def transform(input_grid)` function inside a "
                    "```python code block."
                )
                db.insert_attempt(
                    run_id=run_id,
                    task_id=task_id,
                    test_index=test_idx,
                    attempt=attempt,
                    prompt_chars=prompt_chars,
                    prompt_tokens=prompt_tokens,
                    llm_response=response,
                    extracted_code=None,
                    train_pass=None,
                    test_correct=None,
                    cell_accuracy=None,
                    error_type="extraction_failed",
                    error_msg=error_msg,
                )
                messages = append_retry(messages, response, error_msg)
                print(f"    [{attempt}/{max_retries}] FAIL: code extraction failed")
                continue

            last_code = code

            # Verify on training examples only
            train_result = verify_on_train(
                code, train_examples, execute_transform, timeout
            )

            if not train_result["passed"]:
                error_msg = train_result["error_msg"]
                db.insert_attempt(
                    run_id=run_id,
                    task_id=task_id,
                    test_index=test_idx,
                    attempt=attempt,
                    prompt_chars=prompt_chars,
                    prompt_tokens=prompt_tokens,
                    llm_response=response,
                    extracted_code=code,
                    train_pass=False,
                    test_correct=None,
                    cell_accuracy=None,
                    error_type="train_fail",
                    error_msg=error_msg,
                )
                messages = append_retry(messages, response, error_msg)
                print(f"    [{attempt}/{max_retries}] FAIL: train verification failed")
                continue

            # Run on test input
            test_result = execute_transform(code, test_input, timeout=timeout)
            if not test_result["success"]:
                error_msg = f"Error on test input:\n{test_result['error']}"
                db.insert_attempt(
                    run_id=run_id,
                    task_id=task_id,
                    test_index=test_idx,
                    attempt=attempt,
                    prompt_chars=prompt_chars,
                    prompt_tokens=prompt_tokens,
                    llm_response=response,
                    extracted_code=code,
                    train_pass=True,
                    test_correct=None,
                    cell_accuracy=None,
                    error_type="test_exec_error",
                    error_msg=error_msg,
                )
                messages = append_retry(messages, response, error_msg)
                print(f"    [{attempt}/{max_retries}] FAIL: test execution error")
                continue

            # Compare with expected test output
            cmp = compare_grids(test_result["output"], test_output)

            if cmp["correct"]:
                solved = True
                db.insert_attempt(
                    run_id=run_id,
                    task_id=task_id,
                    test_index=test_idx,
                    attempt=attempt,
                    prompt_chars=prompt_chars,
                    prompt_tokens=prompt_tokens,
                    llm_response=response,
                    extracted_code=code,
                    train_pass=True,
                    test_correct=True,
                    cell_accuracy=1.0,
                    error_type=None,
                    error_msg=None,
                )
                print(f"    [{attempt}/{max_retries}] SOLVED!")
                break

            # Important: do NOT reveal test output in feedback, and do NOT retry
            error_msg = (
                "Model output on the test input was incorrect. "
                "Test-output feedback is not provided to avoid leakage."
            )

            db.insert_attempt(
                run_id=run_id,
                task_id=task_id,
                test_index=test_idx,
                attempt=attempt,
                prompt_chars=prompt_chars,
                prompt_tokens=prompt_tokens,
                llm_response=response,
                extracted_code=code,
                train_pass=True,
                test_correct=False,
                cell_accuracy=cmp["cell_accuracy"],
                error_type="wrong_output",
                error_msg=error_msg,
            )

            print(
                f"    [{attempt}/{max_retries}] FAIL: wrong output "
                f"(cell acc: {cmp['cell_accuracy']:.1%})"
            )

            # Stop here to avoid leaking information from test evaluation
            break

        if solved:
            passed_count += 1
        else:
            all_solved = False

    elapsed = time.time() - start_time

    db.upsert_task(
        run_id=run_id,
        task_id=task_id,
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
        "--dataset",
        choices=["arc1", "arc2"],
        default="arc1",
        help="Dataset to evaluate (default: arc1)",
    )
    parser.add_argument(
        "--split",
        choices=["training", "evaluation"],
        default="training",
        help="Data split (default: training)",
    )
    parser.add_argument(
        "--task-id",
        type=str,
        default=None,
        help="Run a single task by ID",
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=None,
        help="Max number of tasks to evaluate",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=f"Max retry attempts per test case (default: {DEFAULT_MAX_RETRIES})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Code execution timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"LLM temperature (default: {DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="Name for this run (default: timestamp). Reusing a name resumes.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / DATASET_PATHS[args.dataset][args.split]

    # Some ARC-AGI-2 local copies store training JSONs under evaluation/training.
    if args.dataset == "arc2" and args.split == "training" and not data_dir.exists():
        alt_data_dir = project_root / "ARC-AGI-2/data/evaluation/training"
        if alt_data_dir.exists():
            print(f"Warning: default training path not found. Using fallback: {alt_data_dir}")
            data_dir = alt_data_dir

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Run:")
        print("  git clone --depth 1 https://github.com/fchollet/ARC-AGI.git")
        print("  git clone --depth 1 https://github.com/arcprize/ARC-AGI-2.git")
        return

    tasks = load_tasks(str(data_dir))
    if args.task_id:
        if args.task_id not in tasks:
            print(f"Error: Task '{args.task_id}' not found in {data_dir}")
            return
        tasks = {args.task_id: tasks[args.task_id]}

    if args.max_tasks:
        task_ids = list(tasks.keys())[: args.max_tasks]
        tasks = {tid: tasks[tid] for tid in task_ids}

    run_name = args.run_name or datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = project_root / "results" / run_name
    results_dir.mkdir(parents=True, exist_ok=True)
    db_path = results_dir / "results.db"

    db = ResultDB(db_path)
    db.insert_run(
        run_name,
        args.dataset,
        args.split,
        args.max_retries,
        args.timeout,
        args.temperature,
    )

    done = db.get_completed_task_ids(run_name)
    remaining = {tid: td for tid, td in tasks.items() if tid not in done}

    print("=== ARC-AGI Evaluation ===")
    print(f"Dataset:     {args.dataset} / {args.split}")
    print(f"Total tasks: {len(tasks)}")
    if done:
        print(f"Resuming:    {len(done)} already done, {len(remaining)} remaining")
    print(f"Max retries: {args.max_retries}")
    print(f"Timeout:     {args.timeout}s")
    print(f"Temperature: {args.temperature}")
    print(f"Results DB:  {db_path}")
    print()

    solved_so_far = 0
    total_so_far = 0

    for i, (task_id, task_data) in enumerate(remaining.items(), 1):
        n_test = len(task_data["test"])
        n_train = len(task_data["train"])
        print(f"[{i}/{len(remaining)}] Task: {task_id} ({n_train} train, {n_test} test)")

        try:
            result = evaluate_task(
                task_id=task_id,
                task_data=task_data,
                max_retries=args.max_retries,
                timeout=args.timeout,
                temperature=args.temperature,
                db=db,
                run_id=run_name,
            )
        except Exception as e:
            print(f"  ERROR on task {task_id}: {e}\n")
            continue

        total_so_far += 1
        if result["solved"]:
            solved_so_far += 1

        status = "SOLVED" if result["solved"] else "FAILED"
        running_rate = solved_so_far / total_so_far if total_so_far else 0.0
        print(
            f"  {status} ({result['test_cases_passed']}/{result['num_test_cases']} "
            f"test cases, {result['total_time_seconds']:.1f}s) "
            f"| Running: {solved_so_far}/{total_so_far} solved ({running_rate:.0%})\n"
        )

    summary = db.get_summary(run_name)
    print("=== Summary ===")
    print(f"Tasks evaluated: {summary['tasks_evaluated']}")
    print(f"Tasks solved:    {summary['tasks_solved']} ({summary['solve_rate']:.1%})")
    print(f"Test cases:      {summary['test_cases_passed']}/{summary['total_test_cases']}")
    print(f"Results DB:      {db_path}")

    db.close()


if __name__ == "__main__":
    main()