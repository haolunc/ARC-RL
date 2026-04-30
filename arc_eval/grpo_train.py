"""GRPO training entry point for ARC code-generation rewards.

This is intentionally small: it reuses the repo's verifier as an RLVR reward
and delegates the actual optimizer/training loop to Hugging Face TRL.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .code_extract import extract_code
from .config import DATASET_PATHS, DEFAULT_TIMEOUT
from .evaluate import compare_grids
from .prompt import SYSTEM_PROMPT, format_grid
from .safe_exec import execute_transform


def load_tasks(data_dir: str, max_tasks: int | None = None) -> list[dict[str, Any]]:
    """Load ARC JSON tasks into rows suitable for TRL."""
    rows = []
    for path in sorted(Path(data_dir).glob("*.json")):
        with open(path, encoding="utf-8") as f:
            task = json.load(f)
        rows.append(
            {
                "task_id": path.stem,
                "prompt": build_training_prompt(task["train"]),
                "train_examples": task["train"],
            }
        )
        if max_tasks is not None and len(rows) >= max_tasks:
            break
    return rows


def build_training_prompt(train_examples: list[dict]) -> str:
    """Create a prompt whose reward can be computed from train examples only."""
    parts = [SYSTEM_PROMPT, "\nTraining examples:\n"]
    for i, ex in enumerate(train_examples, 1):
        parts.append(f"Example {i}:")
        parts.append(f"Input:\n{format_grid(ex['input'])}")
        parts.append(f"Output:\n{format_grid(ex['output'])}\n")

    parts.append("Infer the rule from the training examples.")
    parts.append("Write exactly one Python function `transform(input_grid)`.")
    return "\n".join(parts)


def _completion_text(completion: Any) -> str:
    """Normalize TRL completion formats to plain text."""
    if isinstance(completion, str):
        return completion
    if isinstance(completion, list) and completion:
        last = completion[-1]
        if isinstance(last, dict):
            return str(last.get("content", ""))
    return str(completion)


def score_code_on_train(
    code: str,
    train_examples: list[dict],
    timeout: int = DEFAULT_TIMEOUT,
) -> float:
    """Return a dense reward in [0, 1], with exact train pass equal to 1."""
    scores = []
    for ex in train_examples:
        result = execute_transform(code, ex["input"], timeout=timeout)
        if not result["success"]:
            scores.append(0.0)
            continue

        cmp = compare_grids(result["output"], ex["output"])
        if cmp["correct"]:
            scores.append(1.0)
        elif cmp["shape_match"]:
            scores.append(0.25 * cmp["cell_accuracy"])
        else:
            scores.append(0.0)

    return sum(scores) / len(scores) if scores else 0.0


def arc_code_reward(
    completions: list[Any],
    train_examples: list[list[dict]],
    **_: Any,
) -> list[float]:
    """Reward function consumed by TRL GRPOTrainer."""
    rewards = []
    for completion, examples in zip(completions, train_examples, strict=False):
        text = _completion_text(completion)
        code = extract_code(text)
        if code is None:
            rewards.append(-0.25)
            continue

        score = score_code_on_train(code, examples)
        rewards.append(1.0 if score == 1.0 else score - 0.1)

    return rewards


def main() -> None:
    parser = argparse.ArgumentParser(description="GRPO post-training for ARC rewards")
    parser.add_argument("--model", default="Qwen/Qwen3.6-35B-A3B")
    parser.add_argument("--output-dir", default="runs/qwen36_arc_grpo")
    parser.add_argument("--dataset", choices=["arc1", "arc2"], default="arc1")
    parser.add_argument("--split", choices=["training", "evaluation"], default="training")
    parser.add_argument("--max-tasks", type=int, default=100)
    parser.add_argument("--num-generations", type=int, default=4)
    parser.add_argument("--max-prompt-length", type=int, default=8192)
    parser.add_argument("--max-completion-length", type=int, default=2048)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--use-vllm", action="store_true")
    parser.add_argument("--vllm-mode", choices=["colocate", "server"], default="server")
    parser.add_argument("--use-peft", action="store_true")
    args = parser.parse_args()

    try:
        from datasets import Dataset
        from trl import GRPOConfig, GRPOTrainer
    except ImportError as e:
        raise SystemExit(
            "Missing TRL. Install a training environment with: "
            "pip install -U 'trl[vllm]' transformers accelerate peft"
        ) from e

    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / DATASET_PATHS[args.dataset][args.split]
    rows = load_tasks(str(data_dir), max_tasks=args.max_tasks)
    train_dataset = Dataset.from_list(rows)

    training_args = GRPOConfig(
        output_dir=args.output_dir,
        learning_rate=args.learning_rate,
        bf16=True,
        num_generations=args.num_generations,
        max_prompt_length=args.max_prompt_length,
        max_completion_length=args.max_completion_length,
        use_vllm=args.use_vllm,
        vllm_mode=args.vllm_mode,
        use_peft=args.use_peft,
        logging_steps=1,
        log_completions=True,
    )

    trainer = GRPOTrainer(
        model=args.model,
        args=training_args,
        train_dataset=train_dataset,
        reward_funcs=arc_code_reward,
    )
    trainer.train()


if __name__ == "__main__":
    main()
