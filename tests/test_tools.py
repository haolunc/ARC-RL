"""Tests for arc.eval.tools."""

from arc.eval.tools import run_python_tool, TOOL_DEFINITION


# --- TOOL_DEFINITION ---

def test_tool_definition_structure():
    assert TOOL_DEFINITION["type"] == "function"
    assert TOOL_DEFINITION["name"] == "python"
    assert "code" in TOOL_DEFINITION["parameters"]["properties"]


# --- run_python_tool ---

def test_run_python_tool_success(task_context):
    result = run_python_tool("print(len(train_inputs))", task_context)
    assert result["success"] is True
    assert str(len(task_context["train_examples"])) in result["output"]


def test_run_python_tool_error(task_context):
    result = run_python_tool("raise ValueError('boom')", task_context)
    assert result["success"] is False
    assert "Error" in result["output"]
    assert "boom" in result["output"]


def test_run_python_tool_numpy(task_context):
    result = run_python_tool("arr = np.array(train_inputs[0])\nprint(arr.shape)", task_context)
    assert result["success"] is True
    assert "3" in result["output"]  # 3x3 grid


def test_run_python_tool_preloaded_vars(task_context):
    result = run_python_tool(
        "print(type(train_inputs).__name__)\n"
        "print(type(train_outputs).__name__)\n"
        "print(type(test_inputs).__name__)\n",
        task_context,
    )
    assert result["success"] is True
    assert "list" in result["output"]
