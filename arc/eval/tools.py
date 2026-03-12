"""Tool definitions and dispatcher for agentic evaluation mode."""

import json

from .safe_exec import execute_transform, execute_analysis
from .evaluate import compare_grids, format_wrong_output_msg, verify_on_train

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Execute arbitrary Python code to analyze the grids. "
                "The following variables are pre-loaded: "
                "train_inputs (list of input grids), "
                "train_outputs (list of output grids), "
                "test_input (the test input grid). "
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
        },
    },
    {
        "type": "function",
        "function": {
            "name": "test_transform",
            "description": (
                "Test a `def transform(input_grid)` function on ALL training examples. "
                "Returns per-example results showing match/no-match with details."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": (
                            "Python code containing a `def transform(input_grid)` function. "
                            "May use standard library and numpy."
                        ),
                    }
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_transform",
            "description": (
                "Submit your final `def transform(input_grid)` function for test evaluation. "
                "Returns only pass/fail (no expected output is shown). "
                "Use this when you are confident your solution is correct."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": (
                            "Python code containing your final `def transform(input_grid)` function."
                        ),
                    }
                },
                "required": ["code"],
            },
        },
    },
]


def execute_tool(tool_name: str, tool_args: dict, task_context: dict) -> dict:
    """Dispatch and execute a tool call.

    Args:
        tool_name: Name of the tool to execute.
        tool_args: Parsed arguments dict.
        task_context: Dict with keys: train_examples, test_input, test_output,
                      timeout, python_path.

    Returns:
        Dict with keys:
            output: str - text result to return to the LLM
            solved: bool | None - True/False for submit_transform, None otherwise
            extracted_code: str | None - the code that was run (for logging)
    """
    train_examples = task_context["train_examples"]
    test_input = task_context["test_input"]
    test_output = task_context["test_output"]
    timeout = task_context["timeout"]
    python_path = task_context["python_path"]
    code = tool_args.get("code", "")

    if tool_name == "run_python":
        result = execute_analysis(
            code, train_examples, test_input, timeout, python_path
        )
        if result["success"]:
            return {"output": result["output"], "solved": None, "extracted_code": code}
        else:
            return {"output": f"Error:\n{result['error']}", "solved": None, "extracted_code": code}

    elif tool_name == "test_transform":
        parts = []
        all_pass = True
        for i, ex in enumerate(train_examples, 1):
            result = execute_transform(code, ex["input"], timeout=timeout, python_path=python_path)
            if not result["success"]:
                parts.append(f"Example {i}: ERROR\n{result['error']}")
                all_pass = False
                break

            cmp = compare_grids(result["output"], ex["output"])
            if cmp["correct"]:
                parts.append(f"Example {i}: PASS")
            else:
                all_pass = False
                detail = format_wrong_output_msg(
                    f"training example {i}", ex["output"], result["output"], cmp
                )
                parts.append(f"Example {i}: FAIL\n{detail}")

        summary = "All training examples passed!" if all_pass else "Some training examples failed."
        output = summary + "\n\n" + "\n\n".join(parts)
        return {"output": output, "solved": None, "extracted_code": code}

    elif tool_name == "submit_transform":
        # First verify on training examples (silent check)
        train_check = verify_on_train(code, train_examples, execute_transform, timeout, python_path=python_path)
        if not train_check["passed"]:
            return {
                "output": "Submission rejected: your code does not pass all training examples. Use test_transform to debug first.",
                "solved": False,
                "extracted_code": code,
            }

        # Run on test input
        test_result = execute_transform(code, test_input, timeout=timeout, python_path=python_path)
        if not test_result["success"]:
            return {
                "output": f"Runtime error on test input:\n{test_result['error']}",
                "solved": False,
                "extracted_code": code,
            }

        cmp = compare_grids(test_result["output"], test_output)
        if cmp["correct"]:
            return {
                "output": "Correct! Your submission passed the test case.",
                "solved": True,
                "extracted_code": code,
            }
        else:
            return {
                "output": "Incorrect. Your submission did not produce the correct output for the test input.",
                "solved": False,
                "extracted_code": code,
            }

    else:
        return {"output": f"Unknown tool: {tool_name}", "solved": None, "extracted_code": None}
