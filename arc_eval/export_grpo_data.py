"""Export logged GPRO rollouts to JSONL for later policy training experiments."""

import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def message_text(messages: list[dict]) -> str:
    parts: list[str] = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        parts.append(f"<{role}>\n{content}")
    return "\n\n".join(parts)


def export_rollouts(run_dir: Path, output_path: Path, min_reward: float | None) -> dict:
    samples_path = run_dir / "gpro_samples.jsonl"
    if not samples_path.exists():
        raise FileNotFoundError(f"Missing samples file: {samples_path}")

    rows = load_jsonl(samples_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    written = 0
    missing_text = 0
    with open(output_path, "w", encoding="utf-8") as out:
        for row in rows:
            total += 1
            reward = row.get("reward")
            if min_reward is not None and isinstance(reward, (int, float)):
                if float(reward) < min_reward:
                    continue

            messages = row.get("messages")
            response = row.get("response")
            if not messages or response is None:
                missing_text += 1
                continue

            out_row = {
                "task_id": row.get("task_id"),
                "test_index": row.get("test_index"),
                "step": row.get("step"),
                "sample_index": row.get("sample_index"),
                "prompt": message_text(messages),
                "messages": messages,
                "completion": response,
                "extracted_code": row.get("extracted_code"),
                "reward": reward,
                "train_pass": row.get("train_pass"),
                "avg_train_cell_accuracy": row.get("avg_train_cell_accuracy"),
                "error_type": row.get("error_type"),
                "error_msg": row.get("error_msg"),
            }
            out.write(json.dumps(out_row, ensure_ascii=False) + "\n")
            written += 1

    return {
        "samples_read": total,
        "rows_written": written,
        "rows_missing_text": missing_text,
        "output_path": str(output_path),
    }


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Export GPRO rollout samples with prompt/response/reward fields. "
            "The source run must be collected with --log-sample-text."
        )
    )
    parser.add_argument("run_dir", type=str, help="Path to results/<run_name>")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSONL path (default: <run_dir>/grpo_rollouts.jsonl)",
    )
    parser.add_argument(
        "--min-reward",
        type=float,
        default=None,
        help="Only export rows with reward >= this value.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    output_path = Path(args.output) if args.output else run_dir / "grpo_rollouts.jsonl"
    summary = export_rollouts(run_dir, output_path, args.min_reward)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
