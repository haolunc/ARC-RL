"""Entry point for ARC-AGI LLM evaluation pipeline."""

import argparse
import json
from pathlib import Path


def load_tasks(data_dir: str) -> dict[str, dict]:
    """Load all ARC tasks from a directory of JSON files.

    Returns: {task_id: {"train": [...], "test": [...]}}
    """
    raise NotImplementedError


def evaluate_single_task(task_id, task_data, client, cfg, db, run_name):
    """Evaluate a single ARC task: prompt -> LLM -> test -> DB."""
    raise NotImplementedError


def main():
    parser = argparse.ArgumentParser(description="ARC-AGI LLM Evaluation Pipeline")
    parser.add_argument("config", type=str, help="Path to config YAML file")
    args = parser.parse_args()
    raise NotImplementedError


if __name__ == "__main__":
    main()
