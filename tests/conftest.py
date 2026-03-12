"""Shared fixtures for ARC eval tests."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "ARC-AGI-2" / "data" / "training"
SOLUTIONS_DIR = ROOT / "reference_solutions" / "solutions"
PYTHON_PATH = "/opt/homebrew/Caskroom/miniforge/base/envs/arc/bin/python"


def load_task(task_id: str) -> dict:
    """Load an ARC task JSON by ID."""
    path = DATA_DIR / f"{task_id}.json"
    return json.loads(path.read_text())


def load_solution(task_id: str) -> str:
    """Load a reference solution by task ID."""
    path = SOLUTIONS_DIR / f"{task_id}.py"
    return path.read_text()


@pytest.fixture
def python_path():
    return PYTHON_PATH


@pytest.fixture
def sample_task():
    """Load task 007bbfb7 (small 3x3 grids)."""
    return load_task("007bbfb7")


@pytest.fixture
def sample_solution():
    """Load reference solution for task 007bbfb7."""
    return load_solution("007bbfb7")


@pytest.fixture
def sample_task_with_solution(sample_task, sample_solution):
    return sample_task, sample_solution


@pytest.fixture
def task_context(sample_task, sample_solution, python_path):
    """Build a task_context dict for tools.execute_tool."""
    return {
        "train_examples": sample_task["train"],
        "test_input": sample_task["test"][0]["input"],
        "test_output": sample_task["test"][0]["output"],
        "timeout": 30,
        "python_path": python_path,
    }
