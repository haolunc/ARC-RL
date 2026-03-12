"""Download verified ARC AGI solutions from HuggingFace.

Source: Trelis/arc-agi-2-reasoning-5 (Apache 2.0)
All solutions are verified correct on both train and test examples.
"""

import os
from pathlib import Path
from datasets import load_dataset

DATASET_NAME = "Trelis/arc-agi-2-reasoning-5"
OUTPUT_DIR = Path(__file__).parent / "solutions"
ARC_DATA_DIRS = [
    Path(__file__).parent.parent / "ARC-AGI" / "data" / "training",
    Path(__file__).parent.parent / "ARC-AGI" / "data" / "evaluation",
    Path(__file__).parent.parent / "ARC-AGI-2" / "data" / "training",
    Path(__file__).parent.parent / "ARC-AGI-2" / "data" / "evaluation",
]


def get_local_task_ids() -> set[str]:
    """Collect all task IDs available in local ARC data."""
    task_ids = set()
    for data_dir in ARC_DATA_DIRS:
        if data_dir.exists():
            for f in data_dir.glob("*.json"):
                task_ids.add(f.stem)
    return task_ids


def main():
    print(f"Loading dataset: {DATASET_NAME}")
    ds = load_dataset(DATASET_NAME, split="train")
    print(f"Total rows: {len(ds)}")

    local_tasks = get_local_task_ids()
    print(f"Local ARC tasks found: {len(local_tasks)}")

    # Group by task_id, keep shortest solution with def transform
    best: dict[str, str] = {}
    skipped_no_transform = 0
    total_with_transform = 0

    for row in ds:
        code = row["code"]
        task_id = row["task_id"]

        if "def transform" not in code:
            skipped_no_transform += 1
            continue

        total_with_transform += 1

        # Pick shortest solution per task (tends to be cleaner)
        if task_id not in best or len(code) < len(best[task_id]):
            best[task_id] = code

    # Save solutions
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    matched_local = 0
    for task_id, code in sorted(best.items()):
        out_path = OUTPUT_DIR / f"{task_id}.py"
        out_path.write_text(code)
        if task_id in local_tasks:
            matched_local += 1

    print(f"\n--- Summary ---")
    print(f"Rows with 'def transform': {total_with_transform}")
    print(f"Rows without 'def transform' (skipped): {skipped_no_transform}")
    print(f"Unique tasks saved: {len(best)}")
    print(f"  - Matched local ARC data: {matched_local}")
    print(f"  - No local match: {len(best) - matched_local}")
    print(f"Solutions saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
