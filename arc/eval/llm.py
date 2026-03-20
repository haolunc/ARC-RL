"""LLM calling logic — sandbox_tools loop, direct mode, and code execution."""

import os
import subprocess
import tempfile
from dataclasses import dataclass


@dataclass
class LLMResult:
    text: str
    usage: dict
    tool_rounds: int


def execute_python(code: str, python_path: str, timeout: int = 30) -> dict:
    """Execute Python code in a subprocess sandbox.

    Returns: {"stdout": str, "stderr": str, "exit_code": int}
    """
    raise NotImplementedError


def call_llm(client, cfg: dict, messages: list[dict]) -> LLMResult:
    """Call LLM based on mode (sandbox_tools or direct). Returns LLMResult."""
    raise NotImplementedError
