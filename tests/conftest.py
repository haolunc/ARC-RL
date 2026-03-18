"""Shared fixtures for ARC eval tests."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "ARC-AGI-2" / "data" / "training"
SOLUTIONS_DIR = ROOT / "reference_solutions" / "solutions"
PYTHON_PATH = "/opt/homebrew/Caskroom/miniforge/base/envs/arc/bin/python"


def pytest_addoption(parser):
    parser.addoption(
        "--endpoint-config",
        action="store",
        default=None,
        help="Path to config YAML for LLM integration tests",
    )


def load_task(task_id: str) -> dict:
    """Load an ARC task JSON by ID."""
    path = DATA_DIR / f"{task_id}.json"
    return json.loads(path.read_text())


def load_solution(task_id: str) -> str:
    """Load a reference solution by task ID.

    Reference solutions define `transform()`. An alias `test_transform = transform`
    is appended so they work with the new driver template.
    """
    path = SOLUTIONS_DIR / f"{task_id}.py"
    code = path.read_text()
    return code + "\ntest_transform = transform\n"


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
def task_context(sample_task, python_path):
    """Build a task_context dict for tools.run_python_tool."""
    return {
        "train_examples": sample_task["train"],
        "test_inputs": [tc["input"] for tc in sample_task["test"]],
        "timeout": 30,
        "python_path": python_path,
    }
