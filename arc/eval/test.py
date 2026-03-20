"""Code extraction, test execution, and grid comparison."""

import json
import re

from arc.eval.llm import execute_python


def extract_code(text: str) -> str | None:
    """Extract test_transform function from LLM text output.

    Returns the code string, or None if no valid test_transform found.
    """
    matches = re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if not matches:
        return None
    for code in reversed(matches):
        if "def test_transform" in code:
            return code.strip()
    return None


def compare_grids(predicted: list[list[int]], expected: list[list[int]]) -> dict:
    """Compare two grids. Returns {"correct": bool, "cell_accuracy": float}."""
    if len(predicted) != len(expected):
        return {"correct": False, "cell_accuracy": 0.0}
    for p_row, e_row in zip(predicted, expected):
        if len(p_row) != len(e_row):
            return {"correct": False, "cell_accuracy": 0.0}
    total = sum(len(row) for row in expected)
    if total == 0:
        return {"correct": True, "cell_accuracy": 1.0}
    matching = sum(
        p == e for p_row, e_row in zip(predicted, expected) for p, e in zip(p_row, e_row)
    )
    accuracy = matching / total
    return {"correct": accuracy == 1.0, "cell_accuracy": accuracy}


def run_tests(code: str, test_cases: list[dict], python_path: str) -> dict:
    """Execute extracted code against all test cases.

    Returns: {"passed": int, "total": int, "correct": bool, "status": str, "details": list}
    """
    script = code + "\n\nimport json\n"
    for tc in test_cases:
        script += f"print(json.dumps(test_transform({tc['input']})))\n"

    exec_result = execute_python(script, python_path)

    total = len(test_cases)
    if exec_result["exit_code"] != 0:
        return {
            "passed": 0, "total": total, "correct": False,
            "status": "error_exec",
            "details": [{"correct": False, "cell_accuracy": 0.0,
                         "error": exec_result["stderr"]}],
        }

    lines = exec_result["stdout"].strip().splitlines()
    if len(lines) != total:
        return {
            "passed": 0, "total": total, "correct": False,
            "status": "error_exec",
            "details": [{"correct": False, "cell_accuracy": 0.0,
                         "error": f"Expected {total} output lines, got {len(lines)}"}],
        }

    details = []
    passed = 0
    for i, (line, tc) in enumerate(zip(lines, test_cases)):
        try:
            predicted = json.loads(line)
        except json.JSONDecodeError as e:
            details.append({"correct": False, "cell_accuracy": 0.0, "error": str(e)})
            continue
        cmp = compare_grids(predicted, tc["output"])
        details.append({**cmp, "error": None})
        if cmp["correct"]:
            passed += 1

    correct = passed == total
    status = "success" if correct else "wrong_answer"
    return {
        "passed": passed, "total": total, "correct": correct,
        "status": status, "details": details,
    }
