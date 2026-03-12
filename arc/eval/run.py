"""CLI entry point for ARC evaluation pipeline."""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from .config import load_config
from .prompt import build_initial_messages, build_agentic_messages, append_retry
from .llm_client import init_client, call_llm
from .code_extract import extract_code, extract_thinking
from .safe_exec import execute_transform
from .evaluate import compare_grids, verify_on_train, format_wrong_output_msg
from .tools import TOOL_DEFINITIONS, execute_tool
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


def _llm_call_kwargs(llm_result, messages=None):
    """Build common kwargs for db.insert_llm_call from an LLMResponse."""
    kwargs = {
        "requested_model": llm_result.requested_model,
        "temperature": llm_result.temperature,
        "response_id": llm_result.response_id,
        "actual_model": llm_result.actual_model,
        "finish_reason": llm_result.finish_reason,
        "llm_response": llm_result.content,
        "input_tokens": llm_result.input_tokens,
        "output_tokens": llm_result.output_tokens,
        "cached_tokens": llm_result.cached_tokens,
        "duration_seconds": llm_result.duration_seconds,
    }
    if messages is not None:
        kwargs["input_messages"] = json.dumps(messages, ensure_ascii=False)
    return kwargs


def _log_api_error(db, run_id, task_id, test_idx, step, messages, error):
    db.insert_llm_call(run_id, task_id, test_idx, step,
                       input_messages=json.dumps(messages, ensure_ascii=False),
                       success=False, error_type="api_error", error_msg=str(error))


def _finalize_task(db, run_id, task_id, all_solved, passed_count, test_cases, start_time, last_code):
    elapsed = time.time() - start_time
    result = {
        "solved": all_solved,
        "test_cases_passed": passed_count,
        "num_test_cases": len(test_cases),
        "total_time_seconds": round(elapsed, 2),
    }
    db.upsert_task(run_id, task_id, solved=all_solved, num_test_cases=len(test_cases),
                   test_cases_passed=passed_count, total_time_seconds=result["total_time_seconds"],
                   final_code=last_code)
    return result


def evaluate_task(
    task_id: str,
    task_data: dict,
    max_retries: int,
    timeout: int,
    temperature: float,
    python_path: str,
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

        # Build initial conversation
        messages = build_initial_messages(train_examples, test_input)
        solved = False

        for attempt in range(1, max_retries + 1):
            # Call LLM
            num_msgs = len([m for m in messages if m["role"] != "system"])
            print(f"    [{attempt}/{max_retries}] Calling LLM ({num_msgs} messages in context)...", flush=True)
            try:
                llm_result = call_llm(messages, temperature=temperature)
            except RuntimeError as e:
                _log_api_error(db, run_id, task_id, test_idx, attempt, messages, e)
                print(f"    [{attempt}/{max_retries}] API error: {e}")
                break

            response = llm_result.content
            print(f"    [{attempt}/{max_retries}] LLM responded "
                  f"({llm_result.duration_seconds:.0f}s, {len(response)} chars, "
                  f"{llm_result.input_tokens or '?'} in / {llm_result.output_tokens or '?'} out)")

            # Extract thinking content for logging
            thinking, _ = extract_thinking(response)

            # Common kwargs for all DB inserts this attempt
            common = _llm_call_kwargs(llm_result, messages)
            common["thinking"] = thinking

            # Extract code
            code = extract_code(response)
            if code is None:
                error_msg = (
                    "Could not extract a valid Python function from your response. "
                    "Please write a `def transform(input_grid)` function inside a "
                    "```python code block."
                )
                db.insert_llm_call(
                    run_id, task_id, test_idx, attempt,
                    **common,
                    error_type="extraction_failed", error_msg=error_msg,
                )
                messages = append_retry(messages, response, error_msg)
                print(f"    [{attempt}/{max_retries}] FAIL: code extraction failed")
                continue

            last_code = code

            # Verify on training examples
            train_result = verify_on_train(
                code, train_examples, execute_transform, timeout,
                python_path=python_path,
            )

            if not train_result["passed"]:
                error_msg = train_result["error_msg"]
                db.insert_llm_call(
                    run_id, task_id, test_idx, attempt,
                    **common, extracted_code=code,
                    train_pass=False, error_type="train_fail", error_msg=error_msg,
                )
                messages = append_retry(messages, response, error_msg)
                print(f"    [{attempt}/{max_retries}] FAIL: train verification failed")
                continue

            # Run on test input
            test_result = execute_transform(code, test_input, timeout=timeout,
                                            python_path=python_path)
            if not test_result["success"]:
                error_msg = f"Error on test input:\n{test_result['error']}"
                db.insert_llm_call(
                    run_id, task_id, test_idx, attempt,
                    **common, extracted_code=code,
                    train_pass=True, error_type="test_exec_error", error_msg=error_msg,
                )
                messages = append_retry(messages, response, error_msg)
                print(f"    [{attempt}/{max_retries}] FAIL: test execution error")
                continue

            # Compare with expected
            cmp = compare_grids(test_result["output"], test_output)

            if cmp["correct"]:
                solved = True
                db.insert_llm_call(
                    run_id, task_id, test_idx, attempt,
                    **common, extracted_code=code,
                    train_pass=True, test_correct=True, cell_accuracy=1.0,
                )
                print(f"    [{attempt}/{max_retries}] SOLVED!")
                break
            else:
                # Restricted feedback: no expected vs actual for test
                feedback_msg = "Your code produced incorrect output for the test input."
                # Full detail logged to DB for analysis
                detail_msg = format_wrong_output_msg(
                    "test input", test_output, test_result["output"], cmp
                )
                db.insert_llm_call(
                    run_id, task_id, test_idx, attempt,
                    **common, extracted_code=code,
                    train_pass=True, test_correct=False,
                    cell_accuracy=cmp["cell_accuracy"],
                    error_type="wrong_output", error_msg=detail_msg,
                )
                messages = append_retry(messages, response, feedback_msg)
                print(f"    [{attempt}/{max_retries}] FAIL: wrong output (cell acc: {cmp['cell_accuracy']:.1%})")

        if solved:
            passed_count += 1
        else:
            all_solved = False

    return _finalize_task(db, run_id, task_id, all_solved, passed_count, test_cases, start_time, last_code)


def _serialize_assistant_msg(llm_result) -> dict:
    """Convert an LLMResponse to a serializable dict for message history."""
    d = {"role": "assistant"}
    if llm_result.content:
        d["content"] = llm_result.content
    if llm_result.tool_calls:
        d["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in llm_result.tool_calls
        ]
    return d


def evaluate_task_agentic(
    task_id: str,
    task_data: dict,
    max_steps: int,
    timeout: int,
    temperature: float,
    python_path: str,
    db: ResultDB,
    run_id: str,
) -> dict:
    """Agentic evaluation: LLM uses tools to explore, test, and submit."""
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

        task_context = {
            "train_examples": train_examples,
            "test_input": test_input,
            "test_output": test_output,
            "timeout": timeout,
            "python_path": python_path,
        }

        messages = build_agentic_messages(train_examples, test_input)
        solved = False

        for step in range(1, max_steps + 1):
            print(f"    [step {step}/{max_steps}] Calling LLM...", flush=True)
            try:
                llm_result = call_llm(
                    messages, tools=TOOL_DEFINITIONS, temperature=temperature
                )
            except RuntimeError as e:
                _log_api_error(db, run_id, task_id, test_idx, step, messages, e)
                print(f"    [step {step}/{max_steps}] API error: {e}")
                break

            # Extract thinking from content
            thinking = None
            if llm_result.content:
                thinking, _ = extract_thinking(llm_result.content)

            # Insert one llm_calls row for this step
            llm_call_id = db.insert_llm_call(
                run_id, task_id, test_idx, step,
                **_llm_call_kwargs(llm_result, messages),
                thinking=thinking,
            )

            # Append assistant message to history
            messages.append(_serialize_assistant_msg(llm_result))

            if llm_result.tool_calls:
                n_tools = len(llm_result.tool_calls)
                print(f"    [step {step}/{max_steps}] LLM made {n_tools} tool call(s) "
                      f"({llm_result.duration_seconds:.0f}s, "
                      f"{llm_result.input_tokens or '?'} in / {llm_result.output_tokens or '?'} out)")

                for tc_idx, tc in enumerate(llm_result.tool_calls):
                    tool_name = tc.function.name
                    try:
                        tool_args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {"code": tc.function.arguments}

                    print(f"      -> {tool_name}", flush=True)
                    t_tool = time.time()
                    result = execute_tool(tool_name, tool_args, task_context)
                    tool_duration = time.time() - t_tool

                    # Append tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result["output"],
                    })

                    # Log tool call to DB
                    is_submit = tool_name == "submit_transform"
                    db.insert_tool_call(
                        llm_call_id, tc_idx,
                        tool_call_id=tc.id,
                        tool_name=tool_name,
                        tool_arguments=tc.function.arguments,
                        tool_output=result["output"],
                        extracted_code=result.get("extracted_code"),
                        test_correct=result["solved"] if is_submit else None,
                        duration_seconds=round(tool_duration, 3),
                    )

                    if is_submit and result["solved"]:
                        last_code = result["extracted_code"]
                        solved = True
                        print(f"    [step {step}/{max_steps}] SOLVED!")
                        break

                if solved:
                    break

                if result.get("extracted_code"):
                    last_code = result["extracted_code"]
            else:
                # Text-only response (thinking aloud)
                content_preview = (llm_result.content or "")[:80]
                print(f"    [step {step}/{max_steps}] Text response "
                      f"({llm_result.duration_seconds:.0f}s): {content_preview}...")

        if solved:
            passed_count += 1
        else:
            all_solved = False

    return _finalize_task(db, run_id, task_id, all_solved, passed_count, test_cases, start_time, last_code)


def main():
    parser = argparse.ArgumentParser(description="ARC-AGI LLM Evaluation Pipeline")
    parser.add_argument(
        "config", type=str,
        help="Path to config YAML file",
    )
    args = parser.parse_args()

    # Load config
    cfg = load_config(args.config)
    project_root = Path(__file__).resolve().parent.parent.parent

    # Initialize LLM client
    ep = cfg["endpoint"]
    init_client(
        base_url=ep["base_url"],
        api_key=ep["api_key"],
        model=ep["model"],
        temperature=ep["temperature"],
        timeout=float(ep["llm_timeout"]),
    )

    python_path = cfg["python_path"]

    # Always read config
    dataset = cfg["data"]["dataset"]
    split = cfg["data"]["split"]
    mode = cfg["eval"]["mode"]
    max_retries = cfg["eval"]["max_retries"]
    max_steps = cfg["eval"]["max_steps"]
    timeout = cfg["eval"]["timeout"]
    temperature = ep["temperature"]
    max_tasks = cfg["data"].get("max_tasks")
    cfg_task_ids = cfg["data"].get("task_ids")

    # Resolve data directory
    data_dir = project_root / cfg["datasets"][dataset][split]
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Run: git clone --depth 1 https://github.com/fchollet/ARC-AGI.git")
        print("     git clone --depth 1 https://github.com/arcprize/ARC-AGI-2.git")
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
    print(f"Run name:    {run_name}")
    print(f"Mode:        {mode}")
    print(f"Dataset:     {dataset} / {split}")
    print(f"Total tasks: {len(tasks)}")
    if done:
        print(f"Resuming:    {len(done)} already done, {len(remaining)} remaining")
    if mode == "agentic":
        print(f"Max steps:   {max_steps}")
    else:
        print(f"Max retries: {max_retries}")
    print(f"Timeout:     {timeout}s")
    print(f"Temperature: {temperature}")
    print(f"Results DB:  {db_path}")
    print()

    # Evaluate
    solved_so_far = 0
    total_so_far = 0
    for i, (task_id, task_data) in enumerate(remaining.items(), 1):
        n_test = len(task_data["test"])
        n_train = len(task_data["train"])
        print(f"[{i}/{len(remaining)}] Task: {task_id} ({n_train} train, {n_test} test)")
        if mode == "agentic":
            result = evaluate_task_agentic(
                task_id, task_data, max_steps, timeout,
                temperature, python_path, db, run_name,
            )
        else:
            result = evaluate_task(
                task_id, task_data, max_retries, timeout,
                temperature, python_path, db, run_name,
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
    print(f"LLM calls:       {summary['total_llm_calls']}")
    print(f"Tokens:          {summary['total_input_tokens']} in / {summary['total_output_tokens']} out"
          + (f" ({summary['total_cached_tokens']} cached)" if summary['total_cached_tokens'] else ""))
    print(f"LLM time:        {summary['total_llm_duration_seconds']:.1f}s")
    print(f"Results DB:      {db_path}")

    db.close()


if __name__ == "__main__":
    main()
