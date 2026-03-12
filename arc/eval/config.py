"""Configuration — loads unified config YAML + .env."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import yaml

_ROOT = Path(__file__).resolve().parent.parent.parent

load_dotenv(_ROOT / ".env")


def load_config(config_path: str) -> dict:
    """Load and validate unified config YAML.

    Returns dict with keys: python_path, datasets, endpoint, data, eval.
    The endpoint dict includes resolved api_key (not just the env var name).
    """
    path = Path(config_path)
    if not path.is_absolute():
        path = _ROOT / path

    if not path.exists():
        print(f"Error: Config file not found: {path}")
        sys.exit(1)

    with open(path) as f:
        cfg = yaml.safe_load(f)

    # Validate required sections
    for section in ("python_path", "datasets", "endpoint", "data", "eval"):
        if section not in cfg:
            print(f"Error: Missing '{section}' in {path}")
            sys.exit(1)

    # Resolve API key from environment variable
    ep = cfg["endpoint"]
    api_key_env = ep["api_key_env"]
    api_key = os.environ.get(api_key_env)
    if not api_key:
        print(f"Error: Environment variable '{api_key_env}' not set (check .env)")
        sys.exit(1)

    ep["api_key"] = api_key
    ep.setdefault("llm_timeout", 180)

    # Eval section defaults
    ev = cfg["eval"]
    _EVAL_DEFAULTS = {"mode": "simple", "max_retries": 5, "max_steps": 20, "timeout": 30}
    for key, default in _EVAL_DEFAULTS.items():
        ev.setdefault(key, default)
    if ev["mode"] not in ("simple", "agentic"):
        print(f"Error: eval.mode must be 'simple' or 'agentic', got '{ev['mode']}'")
        sys.exit(1)

    return cfg
