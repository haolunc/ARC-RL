"""Tool definition and execution for sandbox_tools mode."""

import json

from .safe_exec import execute_analysis

TOOL_DEFINITION = {
    "type": "function",
    "name": "python",
    "description": (
        "Execute Python code. Pre-loaded variables: "
        "train_inputs (list of input grids), train_outputs (list of output grids), "
        "test_inputs (list of test input grids). "
        "numpy is available as np. "
        "Use print() to see results."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute. Use print() for output.",
            }
        },
        "required": ["code"],
    },
}


def extract_tool_code(tool_call) -> str:
    """Extract the code string from a tool call object."""
    try:
        args = json.loads(tool_call.arguments)
        return args.get("code", tool_call.arguments)
    except (json.JSONDecodeError, AttributeError):
        return getattr(tool_call, "arguments", str(tool_call))


def run_python_tool(code: str, task_context: dict) -> dict:
    """Execute Python code via subprocess with pre-loaded grid data."""
    result = execute_analysis(
        code,
        task_context["train_examples"],
        task_context["test_inputs"],
        task_context["timeout"],
        task_context["python_path"],
    )
    output = result["output"] if result["success"] else f"Error:\n{result['error']}"
    return {"success": result["success"], "output": output}
