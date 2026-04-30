
**python_path**: config 中的 `python_path` 指定用于 subprocess 执行 LLM 生成代码的 Python 解释器路径（executor.py 用它来运行代码）。

```python
"""Configuration — loads config YAML + endpoint.yaml + .env."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import yaml

_ROOT = Path(__file__).resolve().parent.parent.parent
_VALID_MODES = ("sandbox_tools", "direct", "tree_search")

EXEC_TIMEOUT = 30
MAX_TOOL_ROUNDS = 12
WARN_THRESHOLD = 5
TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 16384
TOKEN_BUDGET = 120000
_DATA_DIR_TEMPLATE = "ARC-AGI-2/data/{split}"

load_dotenv(_ROOT / ".env")


def load_config(config_path: str) -> dict:
    """Load and validate config YAML, resolving endpoint from endpoint.yaml.

    Returns dict with keys: python_path, endpoint, data, eval.
    The endpoint dict is fully resolved (name → details, api_key resolved).
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
    for section in ("python_path", "endpoint", "data", "eval"):
        if section not in cfg:
            print(f"Error: Missing '{section}' in {path}")
            sys.exit(1)

    # Resolve endpoint name from endpoint.yaml
    endpoint_name = cfg["endpoint"]
    endpoint_yaml = _ROOT / "endpoint.yaml"
    if not endpoint_yaml.exists():
        print(f"Error: endpoint.yaml not found at {endpoint_yaml}")
        sys.exit(1)

    with open(endpoint_yaml) as f:
        endpoints = yaml.safe_load(f).get("endpoints", {})

    if endpoint_name not in endpoints:
        available = ", ".join(endpoints.keys())
        print(f"Error: Endpoint '{endpoint_name}' not found in endpoint.yaml. Available: {available}")
        sys.exit(1)

    ep = endpoints[endpoint_name]
    ep["name"] = endpoint_name

    # Resolve API key from environment variable
    api_key_env = ep.get("api_key_env")
    if api_key_env:
        api_key = os.environ.get(api_key_env)
        if not api_key:
            print(f"Error: Environment variable '{api_key_env}' not set (check .env)")
            sys.exit(1)
        ep["api_key"] = api_key
    else:
        ep["api_key"] = "no-key"

    cfg["endpoint"] = ep

    ev = cfg["eval"]
    if ev["mode"] not in _VALID_MODES:
        print(f"Error: eval.mode must be one of {_VALID_MODES}, got '{ev['mode']}'")
        sys.exit(1)

    if ev["mode"] == "tree_search":
        ts = ev.get("tree_search")
        if not ts:
            print("Error: eval.mode='tree_search' requires eval.tree_search section")
            sys.exit(1)
        for key in ("max_nodes", "max_depth", "min_children", "exploration_weight"):
            if key not in ts:
                print(f"Error: tree_search.{key} is required")
                sys.exit(1)

    return cfg

```
