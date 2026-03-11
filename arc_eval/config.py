"""Configuration constants for ARC evaluation pipeline."""

import os

API_BASE_URL = "http://promaxgb10-d668.eecs.umich.edu:8000/v1"

# Read key from environment variable instead of hardcoding
API_KEY = os.getenv("ARC_API_KEY")

MODEL = "Qwen/Qwen3-VL-30B-A3B-Instruct"

# Use system python on Great Lakes
PYTHON_PATH = "python"

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

DEFAULT_MAX_RETRIES = 2
DEFAULT_TIMEOUT = 120
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 400