"""Safe subprocess execution of LLM-generated code."""

import json
import subprocess
import tempfile
from pathlib import Path

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

ANALYSIS_DRIVER_TEMPLATE = '''\
import sys
import json
import numpy as np

# Pre-loaded grid data
train_inputs = {train_inputs_json}
train_outputs = {train_outputs_json}
test_input = {test_input_json}

{code}
'''


def _truncate(text, max_len):
    if len(text) > max_len:
        return text[:max_len] + "\n... (truncated)"
    return text


def _run_sandboxed(driver_code, python_path, timeout, stdin_data=None):
    """Write driver to tempfile, run in subprocess, return result dict."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir="/tmp"
    ) as f:
        f.write(driver_code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [python_path, tmp_path],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/tmp",
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "", "returncode": -1, "timed_out": True}
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def execute_transform(
    code: str,
    input_grid: list[list[int]],
    timeout: int,
    python_path: str,
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
    result = _run_sandboxed(driver, python_path, timeout, stdin_data=json.dumps(input_grid))

    if result["timed_out"]:
        return {"success": False, "error": f"Execution timed out after {timeout}s"}

    if result["returncode"] != 0:
        error = _truncate(result["stderr"].strip(), 2000)
        return {"success": False, "error": error}

    try:
        output = json.loads(result["stdout"].strip())
        return {"success": True, "output": output}
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": f"Output was not valid JSON: {result['stdout'][:500]}",
        }


def execute_analysis(
    code: str,
    train_examples: list[dict],
    test_input: list[list[int]],
    timeout: int,
    python_path: str,
) -> dict:
    """Run arbitrary analysis code with grid data pre-loaded.

    Returns:
        {{"success": True, "output": stdout_string}} or
        {{"success": False, "error": error_message}}
    """
    driver = ANALYSIS_DRIVER_TEMPLATE.format(
        train_inputs_json=json.dumps([ex["input"] for ex in train_examples]),
        train_outputs_json=json.dumps([ex["output"] for ex in train_examples]),
        test_input_json=json.dumps(test_input),
        code=code,
    )
    result = _run_sandboxed(driver, python_path, timeout)

    if result["timed_out"]:
        return {"success": False, "error": f"Execution timed out after {timeout}s"}

    stdout = _truncate(result["stdout"], 5000)
    stderr = _truncate(result["stderr"].strip(), 2000)

    if result["returncode"] != 0:
        return {"success": False, "error": stderr}

    output = stdout.strip()
    if stderr:
        output += f"\n\nStderr:\n{stderr}"
    return {"success": True, "output": output if output else "(no output)"}
