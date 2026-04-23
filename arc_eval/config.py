"""Configuration constants for ARC evaluation pipeline."""

import os

API_BASE_URL = os.getenv(
    "ARC_API_BASE_URL",
    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

# Read key from environment variable instead of hardcoding
API_KEY = os.getenv("ARC_API_KEY") or os.getenv("DASHSCOPE_API_KEY")

MODEL = os.getenv("ARC_MODEL", "qwen3.5-plus")

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
DEFAULT_TEMPERATURE = 0.0

# GPRO defaults
DEFAULT_GPRO_GROUP_SIZE = 4
DEFAULT_GPRO_STEPS = 3
DEFAULT_GPRO_TEMPERATURE = 0.7

# Output generation budget
DEFAULT_MAX_TOKENS = 400

# Context budgeting
MAX_CONTEXT_TOKENS = 16000
MAX_INPUT_TOKENS = MAX_CONTEXT_TOKENS - DEFAULT_MAX_TOKENS

# Rough token estimate: 1 token ~= 4 chars
CHARS_PER_TOKEN_ESTIMATE = 4

# Safety margin so we do not sit exactly at the limit
TOKEN_BUDGET_MARGIN = 500
SAFE_MAX_INPUT_TOKENS = MAX_INPUT_TOKENS - TOKEN_BUDGET_MARGIN