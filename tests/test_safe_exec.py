"""Tests for arc.eval.safe_exec."""

import pytest

from arc.eval.safe_exec import execute_transform, execute_analysis
from .conftest import load_task, load_solution, PYTHON_PATH


# --- execute_transform ---

def test_execute_transform_identity(python_path):
    code = "def transform(grid):\n    return grid"
    grid = [[1, 2], [3, 4]]
    result = execute_transform(code, grid, timeout=10, python_path=python_path)
    assert result["success"] is True
    assert result["output"] == grid


def test_execute_transform_real_solution(python_path):
    """Run reference solution for 007bbfb7 on its first training input."""
    task = load_task("007bbfb7")
    solution = load_solution("007bbfb7")
    ex = task["train"][0]
    result = execute_transform(solution, ex["input"], timeout=30, python_path=python_path)
    assert result["success"] is True
    assert result["output"] == ex["output"]


def test_execute_transform_real_solution_test(python_path):
    """Run reference solution on the test input."""
    task = load_task("007bbfb7")
    solution = load_solution("007bbfb7")
    result = execute_transform(
        solution, task["test"][0]["input"], timeout=30, python_path=python_path
    )
    assert result["success"] is True
    assert result["output"] == task["test"][0]["output"]


def test_execute_transform_second_task(python_path):
    """Run a different reference solution (00576224) on its data."""
    task = load_task("00576224")
    solution = load_solution("00576224")
    ex = task["train"][0]
    result = execute_transform(solution, ex["input"], timeout=30, python_path=python_path)
    assert result["success"] is True
    assert result["output"] == ex["output"]


def test_execute_transform_numpy(python_path):
    """Code using numpy should work (numpy is imported in driver)."""
    code = (
        "import numpy as np\n"
        "def transform(grid):\n"
        "    arr = np.array(grid)\n"
        "    return arr.tolist()\n"
    )
    grid = [[1, 2], [3, 4]]
    result = execute_transform(code, grid, timeout=10, python_path=python_path)
    assert result["success"] is True
    assert result["output"] == grid


def test_execute_transform_ndarray_output(python_path):
    """Code returning np.array should be auto-converted to list."""
    code = (
        "import numpy as np\n"
        "def transform(grid):\n"
        "    return np.array(grid)\n"
    )
    grid = [[1, 2], [3, 4]]
    result = execute_transform(code, grid, timeout=10, python_path=python_path)
    assert result["success"] is True
    assert result["output"] == grid


def test_execute_transform_runtime_error(python_path):
    code = "def transform(grid):\n    return 1 / 0"
    result = execute_transform(code, [[1]], timeout=10, python_path=python_path)
    assert result["success"] is False
    assert "ZeroDivisionError" in result["error"]


def test_execute_transform_syntax_error(python_path):
    code = "def transform(grid)\n    return grid"  # missing colon
    result = execute_transform(code, [[1]], timeout=10, python_path=python_path)
    assert result["success"] is False
    assert "SyntaxError" in result["error"]


def test_execute_transform_timeout(python_path):
    code = "def transform(grid):\n    while True: pass"
    result = execute_transform(code, [[1]], timeout=2, python_path=python_path)
    assert result["success"] is False
    assert "timed out" in result["error"].lower()


# --- execute_analysis ---

def test_execute_analysis_basic(python_path):
    task = load_task("007bbfb7")
    code = "print(len(train_inputs))"
    result = execute_analysis(
        code, task["train"], task["test"][0]["input"],
        timeout=10, python_path=python_path,
    )
    assert result["success"] is True
    assert str(len(task["train"])) in result["output"]


def test_execute_analysis_preloaded_vars(python_path):
    """Verify that train_inputs, train_outputs, test_input are accessible."""
    task = load_task("007bbfb7")
    code = (
        "print(type(train_inputs).__name__)\n"
        "print(type(train_outputs).__name__)\n"
        "print(type(test_input).__name__)\n"
        "print(len(train_inputs), len(train_outputs))\n"
    )
    result = execute_analysis(
        code, task["train"], task["test"][0]["input"],
        timeout=10, python_path=python_path,
    )
    assert result["success"] is True
    assert "list" in result["output"]


def test_execute_analysis_numpy(python_path):
    """numpy should be available in analysis code."""
    task = load_task("007bbfb7")
    code = "arr = np.array(train_inputs[0])\nprint(arr.shape)"
    result = execute_analysis(
        code, task["train"], task["test"][0]["input"],
        timeout=10, python_path=python_path,
    )
    assert result["success"] is True
    assert "3" in result["output"]  # 3x3 grid


def test_execute_analysis_error(python_path):
    task = load_task("007bbfb7")
    code = "raise ValueError('test error')"
    result = execute_analysis(
        code, task["train"], task["test"][0]["input"],
        timeout=10, python_path=python_path,
    )
    assert result["success"] is False
    assert "test error" in result["error"]


def test_execute_analysis_timeout(python_path):
    task = load_task("007bbfb7")
    code = "while True: pass"
    result = execute_analysis(
        code, task["train"], task["test"][0]["input"],
        timeout=2, python_path=python_path,
    )
    assert result["success"] is False
    assert "timed out" in result["error"].lower()
