"""Tests for arc.eval.evaluate."""

from arc.eval.evaluate import compare_grids, format_wrong_output_msg, verify_on_train
from arc.eval.safe_exec import execute_transform
from .conftest import load_task, load_solution, PYTHON_PATH


# --- compare_grids ---

def test_compare_grids_identical():
    grid = [[1, 2], [3, 4]]
    result = compare_grids(grid, grid)
    assert result["correct"] is True
    assert result["shape_match"] is True
    assert result["cell_accuracy"] == 1.0


def test_compare_grids_shape_mismatch():
    pred = [[1, 2]]
    exp = [[1, 2], [3, 4]]
    result = compare_grids(pred, exp)
    assert result["correct"] is False
    assert result["shape_match"] is False
    assert result["cell_accuracy"] == 0.0
    assert result["predicted_shape"] == [1, 2]
    assert result["expected_shape"] == [2, 2]


def test_compare_grids_partial_match():
    pred = [[1, 2], [3, 0]]
    exp = [[1, 2], [3, 4]]
    result = compare_grids(pred, exp)
    assert result["correct"] is False
    assert result["shape_match"] is True
    assert result["cell_accuracy"] == 0.75


def test_compare_grids_empty():
    result = compare_grids([], [])
    assert result["correct"] is True
    assert result["cell_accuracy"] == 1.0


def test_compare_grids_width_mismatch():
    pred = [[1, 2, 3]]
    exp = [[1, 2]]
    result = compare_grids(pred, exp)
    assert result["correct"] is False
    assert result["shape_match"] is False


# --- format_wrong_output_msg ---

def test_format_wrong_output_msg_shape_mismatch():
    cmp = {
        "correct": False,
        "shape_match": False,
        "cell_accuracy": 0.0,
        "predicted_shape": [1, 2],
        "expected_shape": [2, 2],
    }
    msg = format_wrong_output_msg("test input", [[1, 2], [3, 4]], [[1, 2]], cmp)
    assert "Shape mismatch" in msg
    assert "test input" in msg


def test_format_wrong_output_msg_cell_accuracy():
    cmp = {
        "correct": False,
        "shape_match": True,
        "cell_accuracy": 0.75,
        "predicted_shape": [2, 2],
        "expected_shape": [2, 2],
    }
    msg = format_wrong_output_msg("training example 1", [[1, 2], [3, 4]], [[1, 2], [3, 0]], cmp)
    assert "Cell accuracy" in msg
    assert "75" in msg


# --- verify_on_train ---

def test_verify_on_train_all_pass():
    """Mock execute_fn that returns correct outputs."""
    examples = [
        {"input": [[1]], "output": [[1]]},
        {"input": [[2]], "output": [[2]]},
    ]

    def mock_exec(code, inp, timeout, **kw):
        return {"success": True, "output": inp}

    result = verify_on_train("dummy", examples, mock_exec, timeout=10)
    assert result["passed"] is True
    assert result["error_msg"] is None
    assert len(result["details"]) == 2


def test_verify_on_train_error():
    examples = [{"input": [[1]], "output": [[1]]}]

    def mock_exec(code, inp, timeout, **kw):
        return {"success": False, "error": "SyntaxError: invalid syntax"}

    result = verify_on_train("dummy", examples, mock_exec, timeout=10)
    assert result["passed"] is False
    assert "SyntaxError" in result["error_msg"]


def test_verify_on_train_wrong_output():
    examples = [{"input": [[1]], "output": [[2]]}]

    def mock_exec(code, inp, timeout, **kw):
        return {"success": True, "output": [[9]]}

    result = verify_on_train("dummy", examples, mock_exec, timeout=10)
    assert result["passed"] is False
    assert "Wrong output" in result["error_msg"]


def test_verify_on_train_with_real_data():
    """Use real task data + real execute_transform + reference solution."""
    task = load_task("007bbfb7")
    solution = load_solution("007bbfb7")
    result = verify_on_train(
        solution, task["train"], execute_transform,
        timeout=30, python_path=PYTHON_PATH,
    )
    assert result["passed"] is True
    assert all(d["correct"] for d in result["details"])
