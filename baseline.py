"""
ARC-AGI Baseline: Zero-shot LLM evaluation on ARC tasks.
Uses Qwen3-VL-30B or GPT-oss-120B via VLLM endpoints.
"""

import argparse
import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()

MODEL_CONFIGS = {
    "qwen": {
        "base_url": os.getenv("QWEN_API_BASE"),
        "api_key": os.getenv("QWEN_API_KEY"),
        "model": os.getenv("QWEN_MODEL"),
    },
    "gpt": {
        "base_url": os.getenv("GPT_API_BASE"),
        "api_key": os.getenv("GPT_API_KEY"),
        "model": os.getenv("GPT_MODEL"),
    },
}


def grid_to_str(grid: list[list[int]]) -> str:
    return "\n".join(" ".join(str(c) for c in row) for row in grid)


def build_prompt(task: dict) -> str:
    """Construct the few-shot prompt from train examples + test input."""
    parts = [
        "You are solving an ARC (Abstraction and Reasoning Corpus) puzzle.",
        "Each puzzle has demonstration input-output pairs that reveal a hidden transformation rule.",
        "Study the examples carefully, figure out the rule, then apply it to the test input.",
        "Reply with ONLY the output grid. Format: one row per line, values separated by spaces. "
        "Do NOT include any explanation.\n",
    ]

    for i, pair in enumerate(task["train"], 1):
        parts.append(f"--- Example {i} ---")
        parts.append(f"Input:\n{grid_to_str(pair['input'])}")
        parts.append(f"Output:\n{grid_to_str(pair['output'])}\n")

    test_input = task["test"][0]["input"]
    parts.append("--- Test ---")
    parts.append(f"Input:\n{grid_to_str(test_input)}")
    parts.append("Output:")

    return "\n".join(parts)


def parse_grid(text: str) -> list[list[int]] | None:
    """Try to extract a 2-D integer grid from the model's response."""
    lines = text.strip().splitlines()

    grid = []
    for line in lines:
        nums = re.findall(r"\d+", line)
        if nums:
            grid.append([int(n) for n in nums])

    return grid if grid else None


def grids_equal(a: list[list[int]], b: list[list[int]]) -> bool:
    if len(a) != len(b):
        return False
    return all(row_a == row_b for row_a, row_b in zip(a, b))


def evaluate_task(
    client: OpenAI, model: str, task: dict, task_id: str, max_tokens: int = 2048
) -> dict:
    prompt = build_prompt(task)
    expected = task["test"][0]["output"]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.0,
        )
        raw = response.choices[0].message.content
        predicted = parse_grid(raw)
        correct = predicted is not None and grids_equal(predicted, expected)

        return {
            "task_id": task_id,
            "correct": correct,
            "predicted": predicted,
            "expected": expected,
            "raw_response": raw,
        }

    except Exception as e:
        return {
            "task_id": task_id,
            "correct": False,
            "predicted": None,
            "expected": expected,
            "raw_response": None,
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="ARC-AGI LLM Baseline Evaluation")
    parser.add_argument(
        "--model",
        choices=["qwen", "gpt"],
        default="qwen",
        help="Which model to use (default: qwen)",
    )
    parser.add_argument(
        "--dataset",
        choices=["training", "evaluation"],
        default="evaluation",
        help="Which split to evaluate on (default: evaluation)",
    )
    parser.add_argument(
        "--version",
        choices=["ARC-AGI", "ARC-AGI-2"],
        default="ARC-AGI",
        help="Which ARC version (default: ARC-AGI)",
    )
    parser.add_argument(
        "--num-tasks",
        type=int,
        default=None,
        help="Number of tasks to evaluate (default: all)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save results JSON",
    )
    args = parser.parse_args()

    cfg = MODEL_CONFIGS[args.model]
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
    model_name = cfg["model"]

    data_dir = Path(__file__).parent / args.version / "data" / args.dataset
    task_files = sorted(data_dir.glob("*.json"))
    if args.num_tasks:
        task_files = task_files[: args.num_tasks]

    print(f"Model:   {model_name}")
    print(f"Dataset: {args.version}/{args.dataset} ({len(task_files)} tasks)")
    print("-" * 50)

    results = []
    correct_count = 0

    for tf in tqdm(task_files, desc="Evaluating"):
        task_id = tf.stem
        with open(tf) as f:
            task = json.load(f)

        result = evaluate_task(client, model_name, task, task_id)
        results.append(result)
        if result["correct"]:
            correct_count += 1

        status = "✓" if result["correct"] else "✗"
        tqdm.write(f"  {status} {task_id}")

    accuracy = correct_count / len(results) if results else 0
    print("-" * 50)
    print(f"Accuracy: {correct_count}/{len(results)} = {accuracy:.2%}")

    output_path = args.output or f"results_{args.model}_{args.version}_{args.dataset}.json"
    summary = {
        "model": model_name,
        "dataset": f"{args.version}/{args.dataset}",
        "total": len(results),
        "correct": correct_count,
        "accuracy": accuracy,
        "results": results,
    }
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
