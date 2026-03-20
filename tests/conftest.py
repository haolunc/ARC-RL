import json
from pathlib import Path

import pytest

PUZZLE_DIR = Path(__file__).parent.parent / "ARC-AGI-2" / "data" / "training"
PYTHON_PATH = "/opt/homebrew/Caskroom/miniforge/base/envs/arc/bin/python"


@pytest.fixture
def python_path():
    return PYTHON_PATH


@pytest.fixture
def puzzle_8d5021e8():
    with open(PUZZLE_DIR / "8d5021e8.json") as f:
        return json.load(f)


@pytest.fixture
def puzzle_992798f6():
    with open(PUZZLE_DIR / "992798f6.json") as f:
        return json.load(f)
