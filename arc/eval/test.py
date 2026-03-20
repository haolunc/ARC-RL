"""Code extraction, test execution, and grid comparison."""

import re


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
    raise NotImplementedError
