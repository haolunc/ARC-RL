"""Tests for arc.eval.llm — execute_python and call_llm."""

import json
from pathlib import Path

import pytest

from arc.eval.llm import execute_python, call_llm, LLMResult
from arc.eval.prompt import build_messages

_API_OUTPUT_DIR = Path(__file__).parent / "api_output"


def test_execute_python_hello_world(python_path):
    result = execute_python('print("hello")', python_path)
    assert result["exit_code"] == 0
    assert result["stdout"].strip() == "hello"
    assert result["stderr"] == ""


def test_execute_python_syntax_error(python_path):
    result = execute_python("def f(", python_path)
    assert result["exit_code"] != 0
    assert "SyntaxError" in result["stderr"]


def test_execute_python_runtime_error(python_path):
    result = execute_python("1/0", python_path)
    assert result["exit_code"] != 0
    assert "ZeroDivisionError" in result["stderr"]


def test_execute_python_timeout(python_path):
    result = execute_python("import time; time.sleep(100)", python_path, timeout=1)
    assert result["exit_code"] == -1
    assert "timed out" in result["stderr"].lower()


def test_execute_python_stdout_truncation(python_path):
    code = 'print("x" * 10000)'
    result = execute_python(code, python_path)
    assert result["exit_code"] == 0
    assert len(result["stdout"]) == 5000


def test_execute_python_stderr_truncation(python_path):
    code = 'import sys; sys.stderr.write("e" * 5000)'
    result = execute_python(code, python_path)
    assert len(result["stderr"]) == 2000


def test_execute_python_numpy_available(python_path):
    result = execute_python("import numpy; print(numpy.__version__)", python_path)
    assert result["exit_code"] == 0
    assert result["stdout"].strip()  # version string is non-empty


# --- call_llm tests (require live API) ---

def _build_test_messages(puzzle):
    return build_messages(puzzle["train"], [tc["input"] for tc in puzzle["test"]])


def _save_result(name: str, result: LLMResult):
    """Save API test result to tests/api_output/ for inspection."""
    _API_OUTPUT_DIR.mkdir(exist_ok=True)
    out = _API_OUTPUT_DIR / f"{name}.txt"
    out.write_text(result.text, encoding="utf-8")
    meta = _API_OUTPUT_DIR / f"{name}_meta.json"
    meta.write_text(json.dumps({"usage": result.usage, "tool_rounds": result.tool_rounds}, indent=2))


@pytest.mark.api
def test_call_llm_direct_mode(qwen_client, cfg, puzzle_8d5021e8):
    cfg_direct = {**cfg, "eval": {**cfg["eval"], "mode": "direct"}}
    messages = _build_test_messages(puzzle_8d5021e8)
    result = call_llm(qwen_client, cfg_direct, messages)
    _save_result("direct_8d5021e8", result)
    assert isinstance(result, LLMResult)
    assert len(result.text) > 0
    assert result.tool_rounds == 0
    assert "[Response]" in result.text
    assert "def test_transform" in result.text


@pytest.mark.api
def test_call_llm_sandbox_tools_mode(qwen_client, cfg, puzzle_8d5021e8):
    cfg_tools = {**cfg, "eval": {**cfg["eval"], "mode": "sandbox_tools"}}
    messages = _build_test_messages(puzzle_8d5021e8)
    result = call_llm(qwen_client, cfg_tools, messages)
    _save_result("sandbox_tools_8d5021e8", result)
    assert isinstance(result, LLMResult)
    assert len(result.text) > 0
    assert result.tool_rounds >= 0
    if result.tool_rounds > 0:
        assert "[Tool Call:" in result.text
        assert "[Tool Result]" in result.text
