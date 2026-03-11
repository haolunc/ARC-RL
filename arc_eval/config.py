"""Configuration constants for ARC evaluation pipeline."""

API_BASE_URL = "http://promaxgb10-d668.eecs.umich.edu:8000/v1"
API_KEY = "api_RPnuSxgxJQamqW04ma9uJW27vc4TyBdy"
MODEL = "Qwen/Qwen3-VL-30B-A3B-Instruct"

PYTHON_PATH = "/opt/homebrew/Caskroom/miniforge/base/envs/eecs545/bin/python"

DATASET_PATHS = {
    "arc1": {
        "training": "ARC-AGI/data/training",
        "evaluation": "ARC-AGI/data/evaluation",
    },
    "arc2": {
        "training": "ARC-AGI-2/data/training",
        "evaluation": "ARC-AGI-2/data/evaluation",
    },
}

DEFAULT_MAX_RETRIES = 5
DEFAULT_TIMEOUT = 30
DEFAULT_TEMPERATURE = 0.7
