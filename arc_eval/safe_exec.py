"""Safe subprocess execution of LLM-generated code."""

import json
import subprocess
import tempfile

from .config import PYTHON_PATH, DEFAULT_TIMEOUT

DRIVER_TEMPLATE = '''\
import sys
import json

try:
    import numpy as np
except Exception:
    np = None

{code}

def _call_user_function(input_grid):
    if "transform" in globals() and callable(transform):
        return transform(input_grid)
    if "solve" in globals() and callable(solve):
        return solve(input_grid)
    raise RuntimeError("No callable transform(input_grid) or solve(grid) function found.")

if __name__ == "__main__":
    input_grid = json.loads(sys.stdin.read())
    result = _call_user_function(input_grid)

    # Normalize numpy arrays to Python lists if needed
    if hasattr(result, "tolist"):
        result = result.tolist()

    # Basic validation / normalization to JSON-safe ints
    if not isinstance(result, list):
        raise RuntimeError("Function output is not a list.")
    normalized = []
    for row in result:
        if not isinstance(row, list):
            raise RuntimeError("Function output is not a 2D list.")
        normalized.append([int(c) for c in row])

    print(json.dumps(normalized))
'''


def execute_transform(
    code: str,
    input_grid: list[list[int]],
    timeout: int = DEFAULT_TIMEOUT,
    python_path: str = PYTHON_PATH,
) -> dict:
    """Execute generated ARC code in a subprocess.

    Args:
        code: Python source code containing def transform(...) or def solve(...).
        input_grid: The input grid to pass to the function.
        timeout: Max execution time in seconds.
        python_path: Python interpreter to use.

    Returns:
        {"success": True, "output": grid}
        or
        {"success": False, "error": error_message}
    """
    driver = DRIVER_TEMPLATE.format(code=code)

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(driver)
            tmp_path = f.name

        result = subprocess.run(
            [python_path, tmp_path],
            input=json.dumps(input_grid),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip() or "Unknown execution error"
            if len(error) > 2000:
                error = error[:2000] + "\n... (truncated)"
            return {"success": False, "error": error}

        try:
            output = json.loads(result.stdout.strip())
            return {"success": True, "output": output}
        except json.JSONDecodeError:
            raw = result.stdout.strip()
            if len(raw) > 500:
                raw = raw[:500] + "... (truncated)"
            return {
                "success": False,
                "error": f"Output was not valid JSON: {raw}",
            }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Execution timed out after {timeout}s"}

    finally:
        try:
            import os
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception:
            pass