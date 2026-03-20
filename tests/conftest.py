import json
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent.parent
_PUZZLE_DIR = _ROOT / "ARC-AGI-2" / "data" / "training"
_CONFIG_PATH = _ROOT / "test_config.yaml"


def _load_cfg():
    if not _CONFIG_PATH.exists():
        pytest.skip("test_config.yaml not found — copy config.yaml.example to test_config.yaml and edit")
    from arc.eval.config import load_config
    return load_config(str(_CONFIG_PATH))


@pytest.fixture(scope="session")
def cfg():
    return _load_cfg()


@pytest.fixture(scope="session")
def python_path(cfg):
    return cfg["python_path"]


@pytest.fixture(scope="session")
def qwen_client(cfg):
    from openai import OpenAI
    ep = cfg["endpoint"]
    ev = cfg["eval"]
    return OpenAI(
        base_url=ep["base_url"],
        api_key=ep["api_key"],
        timeout=float(ev.get("llm_timeout", 180)),
    )


@pytest.fixture
def puzzle_8d5021e8():
    with open(_PUZZLE_DIR / "8d5021e8.json") as f:
        return json.load(f)


@pytest.fixture
def puzzle_992798f6():
    with open(_PUZZLE_DIR / "992798f6.json") as f:
        return json.load(f)


@pytest.fixture
def puzzle_8dab14c2():
    with open(_PUZZLE_DIR / "8dab14c2.json") as f:
        return json.load(f)
