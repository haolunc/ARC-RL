"""Tests for arc.eval.llm — execute_python subprocess sandbox."""

from arc.eval.llm import execute_python


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
