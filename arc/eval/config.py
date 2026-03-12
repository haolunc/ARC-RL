"""Configuration — loads .env + config.yaml + endpoint.yaml."""

import os
from pathlib import Path

from dotenv import load_dotenv
import yaml

_ROOT = Path(__file__).resolve().parent.parent.parent

load_dotenv(_ROOT / ".env")

with open(_ROOT / "config.yaml") as f:
    _cfg = yaml.safe_load(f)

with open(_ROOT / "endpoint.yaml") as f:
    _ep_cfg = yaml.safe_load(f)


# --- active endpoint ---
def _load_endpoint(name: str):
    ep = _ep_cfg["endpoints"][name]
    return {
        "base_url": ep["base_url"],
        "api_key": os.environ[ep["api_key_env"]],
        "model": ep["model"],
        "temperature": ep.get("temperature", 0.7),
    }


_active = _load_endpoint(_ep_cfg["active"])

API_BASE_URL = _active["base_url"]
API_KEY = _active["api_key"]
MODEL = _active["model"]
DEFAULT_TEMPERATURE = _active["temperature"]

PYTHON_PATH = _cfg["python_path"]
DATASET_PATHS = _cfg["datasets"]
DEFAULT_MAX_RETRIES = _cfg["defaults"]["max_retries"]
DEFAULT_TIMEOUT = _cfg["defaults"]["timeout"]
