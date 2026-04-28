"""GPRO-style ARC evaluation with Qwen3.5 group sampling."""

import argparse
import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .code_extract import extract_code
from .config import (
    CHARS_PER_TOKEN_ESTIMATE,
    DATASET_PATHS,
    DEFAULT_GPRO_GROUP_SIZE,
    DEFAULT_GPRO_STEPS,
    DEFAULT_GPRO_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT,
    MODEL,
    SAFE_MAX_INPUT_TOKENS,
)
from .db import ResultDB
from .evaluate import compare_grids, verify_on_train
from .llm_client import call_llm
from .prompt import append_retry, build_initial_messages
from .safe_exec import execute_transform


@dataclass
class Candidate:
    sample_index: int
    response: str | None
    code: str | None
    reward: float
    train_pass: bool
    error_type: str | None
    error_msg: str | None
    llm_seconds: float
    response_chars: int
    avg_train_cell_accuracy: float | None


def load_tasks(data_dir: str) -> dict[str, dict]:
    tasks: dict[str, dict] = {}
    data_path = Path(data_dir)
    for f in sorted(data_path.glob("*.json")):
        with open(f, encoding="utf-8") as fp:
            tasks[f.stem] = json.load(fp)
    return tasks


def approx_token_count(messages: list[dict]) -> int:
    total_chars = sum(len(m["content"]) for m in messages)
    return total_chars // CHARS_PER_TOKEN_ESTIMATE


def enforce_context_budget(messages: list[dict]) -> list[dict]:
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


def train_reward(train_result: dict) -> tuple[float, float | None]:
    if train_result["passed"]:
        return 1.0, 1.0

    details = train_result.get("details") or []
    if not details:
        return -0.5, None

    avg_acc = sum(d["cell_accuracy"] for d in details) / len(details)
    return avg_acc - 0.2, avg_acc


def _jsonl_write(fp, row: dict):
    fp.write(json.dumps(row, ensure_ascii=False) + "\n")


def evaluate_task_gpro(
    task_id: str,
    task_data: dict,
    timeout: int,
    temperature: float,
    model: str,
    group_size: int,
    gpro_steps: int,
    max_api_retries: int,
    max_tokens: int,
    log_sample_text: bool,
    db: ResultDB,
    run_id: str,
    samples_fp,
) -> dict:
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

        print(f"  Test case {test_idx + 1}/{len(test_cases)}", flush=True)
        messages = build_initial_messages(train_examples, test_input)
        solved = False

        for step in range(1, gpro_steps + 1):
            messages = enforce_context_budget(messages)
            prompt_chars = sum(len(m["content"]) for m in messages)
            prompt_tokens = approx_token_count(messages)

            print(
                f"    [step {step}/{gpro_steps}] Sampling group of {group_size} "
                f"({prompt_chars} chars, ~{prompt_tokens} tokens)",
                flush=True,
            )

            candidates: list[Candidate] = []

            for sample_index in range(1, group_size + 1):
                t0 = time.time()
                response = None
                code = None
                error_type = None
                error_msg = None
                reward = -1.0
                train_pass = False
                avg_train_acc = None

                try:
                    response = call_llm(
                        messages,
                        temperature=temperature,
                        model=model,
                        max_api_retries=max_api_retries,
                        max_tokens=max_tokens,
                    )
                    code = extract_code(response)

                    if code is None:
                        error_type = "extraction_failed"
                        error_msg = (
                            "Could not extract a valid Python `transform`/`solve` "
                            "function from model response."
                        )
                        reward = -1.0
                    else:
                        train_result = verify_on_train(
                            code, train_examples, execute_transform, timeout
                        )
                        reward, avg_train_acc = train_reward(train_result)
                        train_pass = train_result["passed"]
                        if not train_pass:
                            error_type = "train_fail"
                            error_msg = train_result["error_msg"]

                except RuntimeError as e:
                    error_type = "api_error"
                    error_msg = str(e)
                    reward = -1.2

                llm_seconds = time.time() - t0
                response_chars = len(response) if response else 0

                c = Candidate(
                    sample_index=sample_index,
                    response=response,
                    code=code,
                    reward=reward,
                    train_pass=train_pass,
                    error_type=error_type,
                    error_msg=error_msg,
                    llm_seconds=llm_seconds,
                    response_chars=response_chars,
                    avg_train_cell_accuracy=avg_train_acc,
                )
                candidates.append(c)

                _jsonl_write(
                    samples_fp,
                    {
                        "run_id": run_id,
                        "task_id": task_id,
                        "test_index": test_idx,
                        "step": step,
                        "sample_index": sample_index,
                        "group_size": group_size,
                        "prompt_chars": prompt_chars,
                        "prompt_tokens": prompt_tokens,
                        "llm_seconds": round(llm_seconds, 3),
                        "response_chars": response_chars,
                        "reward": reward,
                        "train_pass": train_pass,
                        "avg_train_cell_accuracy": avg_train_acc,
                        "error_type": error_type,
                        "error_msg": error_msg,
                    }
                    | (
                        {
                            "messages": messages,
                            "response": response,
                            "extracted_code": code,
                        }
                        if log_sample_text
                        else {}
                    ),
                )

            best = max(candidates, key=lambda x: x.reward)
            last_code = best.code or last_code

            db.insert_attempt(
                run_id=run_id,
                task_id=task_id,
                test_index=test_idx,
                attempt=step,
                prompt_chars=prompt_chars,
                prompt_tokens=prompt_tokens,
                llm_response=best.response,
                extracted_code=best.code,
                train_pass=best.train_pass,
                test_correct=None,
                cell_accuracy=best.avg_train_cell_accuracy,
                error_type=best.error_type,
                error_msg=best.error_msg,
            )

            if not best.train_pass or best.code is None:
                fallback_error = best.error_msg or "Best sample failed train verification."
                messages = append_retry(
                    messages,
                    best.response or "",
                    fallback_error,
                )
                print(
                    f"    [step {step}/{gpro_steps}] best reward={best.reward:.3f}, "
                    "train fail -> retry",
                    flush=True,
                )
                continue

            test_result = execute_transform(best.code, test_input, timeout=timeout)
            if not test_result["success"]:
                err = f"Error on test input:\n{test_result['error']}"
                db.insert_attempt(
                    run_id=run_id,
                    task_id=task_id,
                    test_index=test_idx,
                    attempt=step,
                    prompt_chars=prompt_chars,
                    prompt_tokens=prompt_tokens,
                    llm_response=best.response,
                    extracted_code=best.code,
                    train_pass=True,
                    test_correct=None,
                    cell_accuracy=None,
                    error_type="test_exec_error",
                    error_msg=err,
                )
                messages = append_retry(messages, best.response or "", err)
                print(f"    [step {step}/{gpro_steps}] FAIL: test execution error", flush=True)
                continue

            cmp = compare_grids(test_result["output"], test_output)
            if cmp["correct"]:
                solved = True
                db.insert_attempt(
                    run_id=run_id,
                    task_id=task_id,
                    test_index=test_idx,
                    attempt=step,
                    prompt_chars=prompt_chars,
                    prompt_tokens=prompt_tokens,
                    llm_response=best.response,
                    extracted_code=best.code,
                    train_pass=True,
                    test_correct=True,
                    cell_accuracy=1.0,
                    error_type=None,
                    error_msg=None,
                )
                print(f"    [step {step}/{gpro_steps}] SOLVED (best reward={best.reward:.3f})", flush=True)
                break

            db.insert_attempt(
                run_id=run_id,
                task_id=task_id,
                test_index=test_idx,
                attempt=step,
                prompt_chars=prompt_chars,
                prompt_tokens=prompt_tokens,
                llm_response=best.response,
                extracted_code=best.code,
                train_pass=True,
                test_correct=False,
                cell_accuracy=cmp["cell_accuracy"],
                error_type="wrong_output",
                error_msg="Model output on test input was incorrect.",
            )
            print(
                f"    [step {step}/{gpro_steps}] FAIL: wrong output "
                f"(cell acc: {cmp['cell_accuracy']:.1%})",
                flush=True,
            )
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
    parser = argparse.ArgumentParser(description="ARC GPRO Evaluation (Qwen3.5)")
    parser.add_argument("--dataset", choices=["arc1", "arc2"], default="arc1")
    parser.add_argument(
        "--split",
        choices=["training", "evaluation"],
        default="training",
    )
    parser.add_argument("--task-id", type=str, default=None)
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument(
        "--task-start",
        type=int,
        default=None,
        help="1-based inclusive start index in sorted task order.",
    )
    parser.add_argument(
        "--task-end",
        type=int,
        default=None,
        help="1-based inclusive end index in sorted task order.",
    )
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--temperature", type=float, default=DEFAULT_GPRO_TEMPERATURE)
    parser.add_argument("--group-size", type=int, default=DEFAULT_GPRO_GROUP_SIZE)
    parser.add_argument("--gpro-steps", type=int, default=DEFAULT_GPRO_STEPS)
    parser.add_argument("--max-api-retries", type=int, default=2)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--model", type=str, default=MODEL)
    parser.add_argument(
        "--log-sample-text",
        action="store_true",
        help=(
            "Include prompt messages, raw responses, and extracted code in "
            "gpro_samples.jsonl for later GRPO/offline training data export."
        ),
    )
    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="Name for this run (default: timestamp). Reusing a name resumes.",
    )
    args = parser.parse_args()

    if args.group_size <= 0:
        raise ValueError("--group-size must be >= 1")
    if args.gpro_steps <= 0:
        raise ValueError("--gpro-steps must be >= 1")
    if args.task_start is not None and args.task_start <= 0:
        raise ValueError("--task-start must be >= 1")
    if args.task_end is not None and args.task_end <= 0:
        raise ValueError("--task-end must be >= 1")
    if (
        args.task_start is not None
        and args.task_end is not None
        and args.task_start > args.task_end
    ):
        raise ValueError("--task-start must be <= --task-end")

    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / DATASET_PATHS[args.dataset][args.split]

    # Some ARC-AGI-2 local copies store training JSONs under evaluation/training.
    if args.dataset == "arc2" and args.split == "training" and not data_dir.exists():
        alt_data_dir = project_root / "ARC-AGI-2/data/evaluation/training"
        if alt_data_dir.exists():
            print(
                f"Warning: default training path not found. Using fallback: {alt_data_dir}",
                flush=True,
            )
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

    if not args.task_id and (args.task_start is not None or args.task_end is not None):
        task_ids = list(tasks.keys())
        start_index = (args.task_start or 1) - 1
        end_index = args.task_end or len(task_ids)
        selected_ids = task_ids[start_index:end_index]
        tasks = {tid: tasks[tid] for tid in selected_ids}

    if args.max_tasks:
        task_ids = list(tasks.keys())[: args.max_tasks]
        tasks = {tid: tasks[tid] for tid in task_ids}

    run_name = args.run_name or datetime.now().strftime("gpro_%Y%m%d_%H%M%S")
    results_dir = project_root / "results" / run_name
    results_dir.mkdir(parents=True, exist_ok=True)
    db_path = results_dir / "results.db"
    samples_path = results_dir / "gpro_samples.jsonl"

    db = ResultDB(db_path)
    db.insert_run(
        run_name,
        args.dataset,
        args.split,
        args.gpro_steps,
        args.timeout,
        args.temperature,
    )

    done = db.get_completed_task_ids(run_name)
    remaining = {tid: td for tid, td in tasks.items() if tid not in done}

    print("=== ARC GPRO Evaluation ===", flush=True)
    print(f"Dataset:      {args.dataset} / {args.split}", flush=True)
    print(f"Model:        {args.model}", flush=True)
    print(f"Total tasks:  {len(tasks)}", flush=True)
    if done:
        print(f"Resuming:     {len(done)} already done, {len(remaining)} remaining", flush=True)
    print(f"Group size:   {args.group_size}", flush=True)
    print(f"GPRO steps:   {args.gpro_steps}", flush=True)
    print(f"Temperature:  {args.temperature}", flush=True)
    print(f"Log text:     {args.log_sample_text}", flush=True)
    print(f"Timeout:      {args.timeout}s", flush=True)
    print(f"Results DB:   {db_path}", flush=True)
    print(f"Samples JSONL:{samples_path}", flush=True)
    print(flush=True)

    solved_so_far = 0
    total_so_far = 0

    with open(samples_path, "a", encoding="utf-8") as samples_fp:
        for i, (task_id, task_data) in enumerate(remaining.items(), 1):
            n_test = len(task_data["test"])
            n_train = len(task_data["train"])
            print(
                f"[{i}/{len(remaining)}] Task: {task_id} "
                f"({n_train} train, {n_test} test)",
                flush=True,
            )

            try:
                result = evaluate_task_gpro(
                    task_id=task_id,
                    task_data=task_data,
                    timeout=args.timeout,
                    temperature=args.temperature,
                    model=args.model,
                    group_size=args.group_size,
                    gpro_steps=args.gpro_steps,
                    max_api_retries=args.max_api_retries,
                    max_tokens=args.max_tokens,
                    log_sample_text=args.log_sample_text,
                    db=db,
                    run_id=run_name,
                    samples_fp=samples_fp,
                )
            except Exception as e:
                print(f"  ERROR on task {task_id}: {e}\n", flush=True)
                continue

            total_so_far += 1
            if result["solved"]:
                solved_so_far += 1

            status = "SOLVED" if result["solved"] else "FAILED"
            running_rate = solved_so_far / total_so_far if total_so_far else 0.0
            print(
                f"  {status} ({result['test_cases_passed']}/{result['num_test_cases']} "
                f"test cases, {result['total_time_seconds']:.1f}s) "
                f"| Running: {solved_so_far}/{total_so_far} solved ({running_rate:.0%})\n",
                flush=True,
            )

    summary = db.get_summary(run_name)
    summary_payload = {
        "run_id": run_name,
        "dataset": args.dataset,
        "split": args.split,
        "model": args.model,
        "group_size": args.group_size,
        "gpro_steps": args.gpro_steps,
        "task_start": args.task_start,
        "task_end": args.task_end,
        "log_sample_text": args.log_sample_text,
        "temperature": args.temperature,
        "summary": summary,
    }

    summary_path = results_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)

    print("=== Summary ===", flush=True)
    print(f"Tasks evaluated: {summary['tasks_evaluated']}", flush=True)
    print(f"Tasks solved:    {summary['tasks_solved']} ({summary['solve_rate']:.1%})", flush=True)
    print(f"Test cases:      {summary['test_cases_passed']}/{summary['total_test_cases']}", flush=True)
    print(f"Results DB:      {db_path}", flush=True)
    print(f"Summary JSON:    {summary_path}", flush=True)

    db.close()


if __name__ == "__main__":
    main()
