"""Tests for arc.eval.tools."""

from arc.eval.tools import execute_tool, TOOL_DEFINITIONS
from .conftest import load_task, load_solution, PYTHON_PATH


def _ctx(task_id="007bbfb7"):
    """Build a task_context for a given task ID."""
    task = load_task(task_id)
    return {
        "train_examples": task["train"],
        "test_input": task["test"][0]["input"],
        "test_output": task["test"][0]["output"],
        "timeout": 30,
        "python_path": PYTHON_PATH,
    }


# --- TOOL_DEFINITIONS ---

def test_tool_definitions_structure():
    assert len(TOOL_DEFINITIONS) == 3
    names = {t["function"]["name"] for t in TOOL_DEFINITIONS}
    assert names == {"run_python", "test_transform", "submit_transform"}


# --- run_python ---

def test_run_python_success():
    ctx = _ctx()
    result = execute_tool("run_python", {"code": "print(len(train_inputs))"}, ctx)
    assert result["solved"] is None
    assert str(len(ctx["train_examples"])) in result["output"]


def test_run_python_error():
    ctx = _ctx()
    result = execute_tool("run_python", {"code": "raise ValueError('boom')"}, ctx)
    assert result["solved"] is None
    assert "Error" in result["output"]
    assert "boom" in result["output"]


# --- test_transform ---

def test_test_transform_all_pass():
    ctx = _ctx()
    solution = load_solution("007bbfb7")
    result = execute_tool("test_transform", {"code": solution}, ctx)
    assert result["solved"] is None
    assert "All training examples passed!" in result["output"]


def test_test_transform_fail():
    ctx = _ctx()
    code = "def transform(grid):\n    return grid"  # identity won't be correct
    result = execute_tool("test_transform", {"code": code}, ctx)
    assert result["solved"] is None
    assert "Some training examples failed." in result["output"]
    assert "FAIL" in result["output"]


def test_test_transform_error():
    ctx = _ctx()
    code = "def transform(grid):\n    return 1/0"
    result = execute_tool("test_transform", {"code": code}, ctx)
    assert "ERROR" in result["output"]


# --- submit_transform ---

def test_submit_transform_correct():
    ctx = _ctx()
    solution = load_solution("007bbfb7")
    result = execute_tool("submit_transform", {"code": solution}, ctx)
    assert result["solved"] is True
    assert "Correct" in result["output"]


def test_submit_transform_correct_second_task():
    ctx = _ctx("00576224")
    solution = load_solution("00576224")
    result = execute_tool("submit_transform", {"code": solution}, ctx)
    assert result["solved"] is True


def test_submit_transform_fails_training():
    ctx = _ctx()
    code = "def transform(grid):\n    return grid"
    result = execute_tool("submit_transform", {"code": code}, ctx)
    assert result["solved"] is False
    assert "rejected" in result["output"].lower()


def test_submit_transform_wrong_test():
    """Code that passes training but fails test.

    We construct a cheating function that uses json to memorize training outputs
    but returns garbage for unseen inputs.
    """
    ctx = _ctx()
    train = ctx["train_examples"]
    # Build a lookup from json-serialized input to json-serialized output
    import json
    lookup_dict = {}
    for ex in train:
        lookup_dict[json.dumps(ex["input"])] = ex["output"]

    lines = [
        "import json",
        f"_LOOKUP = {json.dumps({k: v for k, v in lookup_dict.items()})}",
        "def transform(grid):",
        "    key = json.dumps(grid)",
        "    if key in _LOOKUP:",
        "        return _LOOKUP[key]",
        "    return [[0]]",
    ]
    code = "\n".join(lines)

    result = execute_tool("submit_transform", {"code": code}, ctx)
    assert result["solved"] is False
    assert "Incorrect" in result["output"]


# --- unknown tool ---

def test_unknown_tool():
    ctx = _ctx()
    result = execute_tool("nonexistent_tool", {}, ctx)
    assert "Unknown tool" in result["output"]
