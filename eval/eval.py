#!/usr/bin/env python3
"""Evaluate ARC-AGI and ARC-AGI-2 by directly calling an OpenAI-compatible model."""

from __future__ import annotations

import argparse
import ast
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


@dataclass
class SplitStats:
    total: int = 0
    correct: int = 0
    api_errors: int = 0
    parse_errors: int = 0
    elapsed_seconds: float = 0.0

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 0.0
        return self.correct / self.total

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "correct": self.correct,
            "accuracy": self.accuracy,
            "api_errors": self.api_errors,
            "parse_errors": self.parse_errors,
            "elapsed_seconds": self.elapsed_seconds,
        }


def format_grid(grid: list[list[int]]) -> str:
    return json.dumps(grid, separators=(",", ":"))


def build_messages(task: dict[str, Any], test_input: list[list[int]]) -> list[dict[str, str]]:
    lines: list[str] = []
    lines.append("You solve ARC tasks.")
    lines.append("Infer the transformation from training examples.")
    lines.append("Return ONLY one JSON 2D integer array for the test output.")
    lines.append("No explanation, no markdown, no extra text.")
    lines.append("")
    lines.append("Training examples:")
    for i, ex in enumerate(task["train"], 1):
        lines.append(f"Example {i} input: {format_grid(ex['input'])}")
        lines.append(f"Example {i} output: {format_grid(ex['output'])}")
    lines.append("")
    lines.append(f"Test input: {format_grid(test_input)}")
    lines.append("Test output:")

    return [
        {
            "role": "system",
            "content": "You are a careful ARC puzzle solver that returns valid JSON only.",
        },
        {
            "role": "user",
            "content": "\n".join(lines),
        },
    ]


def get_model_id(base_url: str, requested_model: str | None, headers: dict[str, str], timeout: int) -> str:
    if requested_model:
        return requested_model
    resp = requests.get(f"{base_url}/models", headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("data", [])
    if not items:
        raise RuntimeError("No models found from /v1/models")
    model_id = items[0].get("id")
    if not model_id:
        raise RuntimeError("Invalid /v1/models response: missing data[0].id")
    return model_id


def extract_first_array_candidate(text: str) -> str | None:
    start = text.find("[")
    if start < 0:
        return None
    depth = 0
    in_str = False
    escape = False
    for i, ch in enumerate(text[start:], start=start):
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def parse_grid_from_text(text: str) -> list[list[int]]:
    txt = text.strip()
    if "```" in txt:
        parts = txt.split("```")
        # Prefer first fenced block body if present.
        if len(parts) >= 3:
            txt = parts[1]
            if "\n" in txt:
                txt = txt.split("\n", 1)[1]
            txt = txt.strip()

    candidate = extract_first_array_candidate(txt)
    if candidate is None:
        raise ValueError("No JSON array found in model response")

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        parsed = ast.literal_eval(candidate)

    if not isinstance(parsed, list) or not parsed or not all(isinstance(r, list) for r in parsed):
        raise ValueError("Parsed output is not a non-empty 2D array")
    if not all(parsed):
        raise ValueError("Parsed output has empty row")

    width = len(parsed[0])
    for row in parsed:
        if len(row) != width:
            raise ValueError("Row widths are inconsistent")
        for v in row:
            if not isinstance(v, int):
                raise ValueError("Grid contains non-integer values")
            if v < 0 or v > 9:
                raise ValueError("Grid values must be in [0, 9]")
    return parsed


def call_model(
    base_url: str,
    model: str,
    headers: dict[str, str],
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    resp = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def evaluate_split(
    split_dir: Path,
    base_url: str,
    model: str,
    headers: dict[str, str],
    timeout: int,
    temperature: float,
    max_tokens: int,
    max_tasks: int | None,
    progress_every: int,
) -> SplitStats:
    stats = SplitStats()
    files = sorted(split_dir.glob("*.json"))
    if max_tasks is not None:
        files = files[:max_tasks]

    t0 = time.time()
    for file_idx, file_path in enumerate(files, 1):
        task = json.loads(file_path.read_text())
        for test_ex in task["test"]:
            stats.total += 1
            messages = build_messages(task, test_ex["input"])
            try:
                content = call_model(
                    base_url=base_url,
                    model=model,
                    headers=headers,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
            except Exception:
                stats.api_errors += 1
                continue

            try:
                pred_grid = parse_grid_from_text(content)
            except Exception:
                stats.parse_errors += 1
                continue

            if pred_grid == test_ex["output"]:
                stats.correct += 1

        if progress_every > 0 and file_idx % progress_every == 0:
            elapsed = time.time() - t0
            print(
                f"[{split_dir.name}] {file_idx}/{len(files)} tasks | "
                f"acc={stats.accuracy:.4f} ({stats.correct}/{stats.total}) | "
                f"api_err={stats.api_errors} parse_err={stats.parse_errors} | "
                f"elapsed={elapsed:.1f}s",
                flush=True,
            )

    stats.elapsed_seconds = time.time() - t0
    return stats


def evaluate_dataset(
    dataset_name: str,
    data_root: Path,
    base_url: str,
    model: str,
    headers: dict[str, str],
    timeout: int,
    temperature: float,
    max_tokens: int,
    max_tasks: int | None,
    progress_every: int,
) -> dict[str, Any]:
    training_dir = data_root / "training"
    evaluation_dir = data_root / "evaluation"
    if not training_dir.exists() or not evaluation_dir.exists():
        raise FileNotFoundError(f"Dataset path missing split dirs: {data_root}")

    print(f"\n=== Evaluating {dataset_name} ===", flush=True)
    train_stats = evaluate_split(
        split_dir=training_dir,
        base_url=base_url,
        model=model,
        headers=headers,
        timeout=timeout,
        temperature=temperature,
        max_tokens=max_tokens,
        max_tasks=max_tasks,
        progress_every=progress_every,
    )
    test_stats = evaluate_split(
        split_dir=evaluation_dir,
        base_url=base_url,
        model=model,
        headers=headers,
        timeout=timeout,
        temperature=temperature,
        max_tokens=max_tokens,
        max_tasks=max_tasks,
        progress_every=progress_every,
    )
    return {
        "dataset": dataset_name,
        "train": train_stats.to_dict(),
        "test": test_stats.to_dict(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate ARC-AGI and ARC-AGI-2 via direct model calls.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1", help="OpenAI-compatible base URL")
    parser.add_argument("--model", default=None, help="Model id. If omitted, auto-detect from /v1/models")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""), help="Optional API key")
    parser.add_argument("--arc1-root", default="ARC-AGI/data", help="ARC-AGI data root")
    parser.add_argument("--arc2-root", default="ARC-AGI-2/data", help="ARC-AGI-2 data root")
    parser.add_argument("--timeout", type=int, default=120, help="Request timeout seconds")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature")
    parser.add_argument("--max-tokens", type=int, default=512, help="Max completion tokens")
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=None,
        help="Optional cap for tasks per split (debug). Default: all tasks",
    )
    parser.add_argument("--progress-every", type=int, default=20, help="Progress interval (tasks)")
    parser.add_argument("--output", default=None, help="Optional output json path")
    return parser.parse_args()


def print_summary(results: dict[str, Any]) -> None:
    try:
        from rich.console import Console
        from rich.table import Table
    except Exception:
        print("\n=== Summary ===")
        for ds in results["results"]:
            print(
                f"{ds['dataset']}: "
                f"train_acc={ds['train']['accuracy']:.4f} ({ds['train']['correct']}/{ds['train']['total']}), "
                f"test_acc={ds['test']['accuracy']:.4f} ({ds['test']['correct']}/{ds['test']['total']}), "
                f"train_time={ds['train']['elapsed_seconds']:.1f}s, "
                f"test_time={ds['test']['elapsed_seconds']:.1f}s"
            )
        return

    table = Table(title=f"ARC Evaluation Summary ({results['model']})")
    table.add_column("Dataset", style="bold cyan")
    table.add_column("Train Acc", justify="right")
    table.add_column("Train Correct", justify="right")
    table.add_column("Train Time", justify="right")
    table.add_column("Test Acc", justify="right")
    table.add_column("Test Correct", justify="right")
    table.add_column("Test Time", justify="right")

    for ds in results["results"]:
        table.add_row(
            ds["dataset"],
            f"{ds['train']['accuracy']:.4f}",
            f"{ds['train']['correct']}/{ds['train']['total']}",
            f"{ds['train']['elapsed_seconds']:.1f}s",
            f"{ds['test']['accuracy']:.4f}",
            f"{ds['test']['correct']}/{ds['test']['total']}",
            f"{ds['test']['elapsed_seconds']:.1f}s",
        )

    Console().print(table)


def main() -> None:
    args = parse_args()
    headers = {"Content-Type": "application/json"}
    if args.api_key:
        headers["Authorization"] = f"Bearer {args.api_key}"

    model = get_model_id(args.base_url, args.model, headers, args.timeout)
    print(f"Using model: {model}", flush=True)

    arc1_result = evaluate_dataset(
        dataset_name="ARC-AGI",
        data_root=Path(args.arc1_root),
        base_url=args.base_url,
        model=model,
        headers=headers,
        timeout=args.timeout,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        max_tasks=args.max_tasks,
        progress_every=args.progress_every,
    )
    arc2_result = evaluate_dataset(
        dataset_name="ARC-AGI-2",
        data_root=Path(args.arc2_root),
        base_url=args.base_url,
        model=model,
        headers=headers,
        timeout=args.timeout,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        max_tasks=args.max_tasks,
        progress_every=args.progress_every,
    )

    results = {
        "model": model,
        "base_url": args.base_url,
        "args": vars(args),
        "results": [arc1_result, arc2_result],
    }

    print_summary(results)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
        print(f"Saved results to: {out_path}")


if __name__ == "__main__":
    main()
