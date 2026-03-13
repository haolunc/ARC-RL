"""
End-to-end pipeline: object extraction -> role induction ->
structured LLM synthesis -> verification (with retry).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

from .grid_utils import Grid, extract_objects, describe_objects, grids_equal
from .role_inducer import analyze_task
from .llm_synthesizer import (
    get_client,
    build_role_aware_prompt,
    build_verification_retry_prompt,
    call_llm,
    parse_grid_response,
)
from .verifier import verify, score_hypothesis, hamming_similarity

load_dotenv()


def solve_task(
    task: dict,
    task_id: str,
    client,
    model: str,
    max_retries: int = 1,
) -> dict:
    """
    Solve a single ARC task using role-induction pipeline.
    1. Analyze task -> extract objects and assign roles
    2. Build structured prompt
    3. Call LLM
    4. Verify; retry with feedback if wrong
    """
    analysis = analyze_task(task, task_id)

    test_input = task["test"][0]["input"]
    test_expected = task["test"][0]["output"]

    test_objects = extract_objects(test_input)
    test_objects_desc = describe_objects(test_objects)

    prompt = build_role_aware_prompt(analysis, test_input, test_objects_desc)

    attempts = []
    best_predicted = None
    best_similarity = -1.0

    for attempt in range(1 + max_retries):
        try:
            if attempt == 0:
                current_prompt = prompt
            else:
                prev = attempts[-1]
                current_prompt = build_verification_retry_prompt(
                    prompt, prev["raw_response"], prev["feedback"]
                )

            raw = call_llm(client, model, current_prompt)
            predicted = parse_grid_response(raw)
            correct, feedback = verify(predicted, test_expected)
            sim = hamming_similarity(predicted, test_expected)

            attempts.append({
                "attempt": attempt,
                "correct": correct,
                "hamming_similarity": sim,
                "feedback": feedback,
                "raw_response": raw,
                "prompt_length": len(current_prompt),
            })

            if sim > best_similarity:
                best_similarity = sim
                best_predicted = predicted

            if correct:
                break

        except Exception as e:
            attempts.append({
                "attempt": attempt,
                "correct": False,
                "error": str(e),
                "raw_response": None,
            })

    final_correct = any(a.get("correct", False) for a in attempts)

    return {
        "task_id": task_id,
        "correct": final_correct,
        "num_attempts": len(attempts),
        "best_hamming": round(best_similarity, 4),
        "predicted": best_predicted,
        "expected": test_expected,
        "attempts": attempts,
        "num_input_objects": sum(len(ex.input_objects) for ex in analysis.examples),
        "num_roles": len({
            ro.role_id
            for ex in analysis.examples
            for ro in ex.input_roles
            if ro.role_id >= 0
        }),
        "global_pattern": analysis.global_pattern,
    }


def main():
    parser = argparse.ArgumentParser(
        description="ARC Role-Induction Pipeline Evaluation"
    )
    parser.add_argument(
        "--model", choices=["qwen", "gpt"], default="qwen",
        help="Which model to use (default: qwen)",
    )
    parser.add_argument(
        "--dataset", choices=["training", "evaluation"], default="evaluation",
        help="Which split (default: evaluation)",
    )
    parser.add_argument(
        "--version", choices=["ARC-AGI", "ARC-AGI-2"], default="ARC-AGI",
        help="Which ARC version (default: ARC-AGI)",
    )
    parser.add_argument(
        "--num-tasks", type=int, default=None,
        help="Number of tasks to evaluate (default: all)",
    )
    parser.add_argument(
        "--max-retries", type=int, default=1,
        help="Max verification retries per task (default: 1)",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Path to save results JSON",
    )
    args = parser.parse_args()

    client, model_name = get_client(args.model)

    data_dir = Path(__file__).parent.parent / args.version / "data" / args.dataset
    task_files = sorted(data_dir.glob("*.json"))
    if args.num_tasks:
        task_files = task_files[: args.num_tasks]

    print(f"Model:       {model_name}")
    print(f"Dataset:     {args.version}/{args.dataset} ({len(task_files)} tasks)")
    print(f"Max retries: {args.max_retries}")
    print("-" * 60)

    results = []
    correct_count = 0
    total_sim = 0.0

    for tf in tqdm(task_files, desc="Evaluating"):
        task_id = tf.stem
        with open(tf) as f:
            task = json.load(f)

        result = solve_task(task, task_id, client, model_name, args.max_retries)
        results.append(result)

        if result["correct"]:
            correct_count += 1
        total_sim += result["best_hamming"]

        status = "✓" if result["correct"] else "✗"
        sim = result["best_hamming"]
        tqdm.write(f"  {status} {task_id} (sim={sim:.2%}, attempts={result['num_attempts']})")

    accuracy = correct_count / len(results) if results else 0
    avg_sim = total_sim / len(results) if results else 0

    print("-" * 60)
    print(f"Exact match accuracy: {correct_count}/{len(results)} = {accuracy:.2%}")
    print(f"Avg cell similarity:  {avg_sim:.2%}")

    output_path = args.output or f"results_role_{args.model}_{args.version}_{args.dataset}.json"
    summary = {
        "model": model_name,
        "method": "role_induction",
        "dataset": f"{args.version}/{args.dataset}",
        "max_retries": args.max_retries,
        "total": len(results),
        "correct": correct_count,
        "accuracy": accuracy,
        "avg_hamming_similarity": round(avg_sim, 4),
        "results": results,
    }
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
