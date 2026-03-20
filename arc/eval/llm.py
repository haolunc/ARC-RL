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
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [python_path, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir(),
        )
        return {
            "stdout": result.stdout[:5000],
            "stderr": result.stderr[:2000],
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Execution timed out", "exit_code": -1}
    finally:
        os.unlink(tmp_path)


def call_llm(client, cfg: dict, messages: list[dict]) -> LLMResult:
    """Call LLM based on mode (sandbox_tools or direct). Returns LLMResult."""
    raise NotImplementedError
