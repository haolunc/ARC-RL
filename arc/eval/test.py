"""Code extraction, test execution, and grid comparison."""

import re


def extract_code(text: str) -> str | None:
    """Extract test_transform function from LLM text output.

    Returns the code string, or None if no valid test_transform found.
    """
    raise NotImplementedError


def compare_grids(predicted: list[list[int]], expected: list[list[int]]) -> dict:
    """Compare two grids. Returns {"correct": bool, "cell_accuracy": float}."""
    raise NotImplementedError


def run_tests(code: str, test_cases: list[dict], python_path: str) -> dict:
    """Execute extracted code against all test cases.

    Returns: {"passed": int, "total": int, "correct": bool, "status": str, "details": list}
    """
    raise NotImplementedError
