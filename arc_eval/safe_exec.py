"""Safe subprocess execution of LLM-generated code."""

import json
import subprocess
import tempfile
from pathlib import Path

from .config import PYTHON_PATH, DEFAULT_TIMEOUT

DRIVER_TEMPLATE = '''\
import sys
import json
import numpy as np

{code}

if __name__ == "__main__":
    input_grid = json.loads(sys.stdin.read())
    result = transform(input_grid)
    # Normalize output to plain list of lists of ints
    if hasattr(result, "tolist"):
        result = result.tolist()
    result = [[int(c) for c in row] for row in result]
    print(json.dumps(result))
'''


def execute_transform(
    code: str,
    input_grid: list[list[int]],
    timeout: int = DEFAULT_TIMEOUT,
    python_path: str = PYTHON_PATH,
) -> dict:
    """Execute a transform function in a subprocess.

    Args:
        code: Python source code containing def transform(...).
        input_grid: The input grid to pass to the function.
        timeout: Max execution time in seconds.
        python_path: Path to Python interpreter.

    Returns:
        {"success": True, "output": grid} or
        {"success": False, "error": error_message}
    """
    driver = DRIVER_TEMPLATE.format(code=code)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir="/tmp"
    ) as f:
        f.write(driver)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [python_path, tmp_path],
            input=json.dumps(input_grid),
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/tmp",
        )

        if result.returncode != 0:
            error = result.stderr.strip()
            # Truncate very long tracebacks
            if len(error) > 2000:
                error = error[:2000] + "\n... (truncated)"
            return {"success": False, "error": error}

        try:
            output = json.loads(result.stdout.strip())
            return {"success": True, "output": output}
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Output was not valid JSON: {result.stdout[:500]}",
            }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Execution timed out after {timeout}s"}
    finally:
        Path(tmp_path).unlink(missing_ok=True)
