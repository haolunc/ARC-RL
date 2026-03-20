"""Tests for arc.eval.test — code extraction and grid comparison."""

from arc.eval.llm import extract_code
from arc.eval.test import compare_grids, run_tests


# --- extract_code tests ---

def test_extract_code_single_block():
    text = """Here is the solution:

```python
def test_transform(input_grid):
    return input_grid
```
"""
    code = extract_code(text)
    assert code is not None
    assert "def test_transform" in code


def test_extract_code_multiple_blocks_prefers_last():
    text = """Let me explore first:

```python
# exploratory analysis
for row in grid:
    print(row)
```

Draft attempt:

```python
def test_transform(input_grid):
    return [[0]]
```

After more analysis, final answer:

```python
def test_transform(input_grid):
    return [row[::-1] for row in input_grid]
```
"""
    code = extract_code(text)
    assert "row[::-1]" in code


def test_extract_code_no_test_transform():
    text = """Here is some code:

```python
import numpy as np
x = np.array([1, 2, 3])
print(x)
```
"""
    assert extract_code(text) is None


def test_extract_code_no_code_blocks():
    text = "The answer is to flip the grid horizontally."
    assert extract_code(text) is None


def test_extract_code_mixed_languages():
    text = """Here is the JSON output:

```json
{"result": [1, 2, 3]}
```

And the Python solution:

```python
def test_transform(input_grid):
    return input_grid
```
"""
    code = extract_code(text)
    assert code is not None
    assert "def test_transform" in code
    assert "json" not in code.lower() or "import json" in code


def test_extract_code_strips_whitespace():
    text = """```python

  def test_transform(input_grid):
      return input_grid

```"""
    code = extract_code(text)
    assert not code.startswith("\n")
    assert not code.endswith("\n")


# --- compare_grids tests ---

def test_compare_grids_identical():
    grid = [[1, 2], [3, 4]]
    result = compare_grids(grid, grid)
    assert result["correct"] is True
    assert result["cell_accuracy"] == 1.0


def test_compare_grids_shape_mismatch_rows():
    result = compare_grids([[1, 2]], [[1, 2], [3, 4]])
    assert result["correct"] is False
    assert result["cell_accuracy"] == 0.0


def test_compare_grids_shape_mismatch_cols():
    result = compare_grids([[1, 2, 3]], [[1, 2]])
    assert result["correct"] is False
    assert result["cell_accuracy"] == 0.0


def test_compare_grids_partial_match():
    predicted = [[1, 2], [3, 4]]
    expected = [[1, 0], [3, 0]]
    result = compare_grids(predicted, expected)
    assert result["correct"] is False
    assert result["cell_accuracy"] == 0.5


def test_compare_grids_all_wrong():
    predicted = [[1, 1], [1, 1]]
    expected = [[0, 0], [0, 0]]
    result = compare_grids(predicted, expected)
    assert result["correct"] is False
    assert result["cell_accuracy"] == 0.0


def test_compare_grids_single_cell():
    assert compare_grids([[5]], [[5]])["correct"] is True
    assert compare_grids([[5]], [[0]])["correct"] is False


# --- run_tests tests ---

_CORRECT_8D5021E8 = """\
def test_transform(input_grid):
    mirrored = [row[::-1] + row for row in input_grid]
    return mirrored * 3
"""

_CORRECT_8D5021E8_BRANCHING = """\
def test_transform(input_grid):
    first_row_all_zeros = all(x == 0 for x in input_grid[0])
    if first_row_all_zeros:
        row0 = input_grid[1] + input_grid[2]
        row1 = input_grid[2] + input_grid[1]
        row2 = input_grid[0] + input_grid[0]
        block_A = [row0, row1, row2]
        block_B = [block_A[2], block_A[1], block_A[0]]
        output = block_A + block_B + block_A
    else:
        block_A = []
        for row in input_grid:
            flipped_row = row[::-1]
            new_row = flipped_row + row
            block_A.append(new_row)
        output = block_A + block_A + block_A
    return output
"""

_WRONG_CODE = """\
def test_transform(input_grid):
    return [[0]]
"""

_ERROR_CODE = """\
def test_transform(input_grid):
    raise ValueError("oops")
"""


def test_run_tests_correct_answer(python_path, puzzle_8d5021e8):
    result = run_tests(_CORRECT_8D5021E8, puzzle_8d5021e8["test"], python_path)
    assert result["status"] == "success"
    assert result["passed"] == 1
    assert result["total"] == 1
    assert result["correct"] is True


def test_run_tests_correct_answer_branching(python_path, puzzle_8d5021e8):
    result = run_tests(_CORRECT_8D5021E8_BRANCHING, puzzle_8d5021e8["test"], python_path)
    assert result["status"] == "success"
    assert result["passed"] == 1
    assert result["total"] == 1
    assert result["correct"] is True


def test_run_tests_wrong_answer(python_path, puzzle_8d5021e8):
    result = run_tests(_WRONG_CODE, puzzle_8d5021e8["test"], python_path)
    assert result["status"] == "wrong_answer"
    assert result["passed"] == 0
    assert result["correct"] is False


def test_run_tests_runtime_error(python_path, puzzle_8d5021e8):
    result = run_tests(_ERROR_CODE, puzzle_8d5021e8["test"], python_path)
    assert result["status"] == "error_exec"


def test_run_tests_json_parse_failure(python_path, puzzle_8d5021e8):
    bad_code = """\
def test_transform(input_grid):
    print("extra garbage")
    return input_grid
"""
    result = run_tests(bad_code, puzzle_8d5021e8["test"], python_path)
    assert result["status"] == "error_exec"


# --- run_tests: multiple test cases (8dab14c2 has 4) ---

# Returns the expected output for the *first* test case only;
# the remaining three will mismatch → passed=1, total=4.
_PARTIAL_8DAB14C2 = """\
def test_transform(input_grid):
    return [
        [8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8],
        [8,8,8,8,8,1,8,8,8,8,8,8,8,8,8,8],
        [8,8,1,1,1,1,1,1,1,1,8,1,1,1,8,8],
        [8,8,1,1,1,1,1,1,1,1,1,1,1,1,8,8],
        [8,8,1,1,1,1,1,1,1,1,1,1,1,1,8,8],
        [8,8,1,1,1,1,1,1,1,1,1,1,1,1,8,8],
        [8,1,1,1,1,8,1,1,1,1,1,1,1,8,8,8],
        [8,8,8,8,8,8,8,8,8,8,1,1,1,1,8,8],
        [8,8,8,8,8,8,8,8,8,8,8,1,1,1,8,8],
        [8,8,8,8,8,8,8,8,8,8,8,1,1,1,8,8],
        [8,8,8,8,8,8,8,8,8,8,8,1,1,1,8,8],
        [8,8,8,8,8,8,8,8,8,8,8,8,1,1,1,8],
        [8,8,8,8,8,8,8,8,8,8,8,1,1,1,8,8],
        [8,8,8,8,8,8,8,8,8,8,8,1,1,1,8,8],
        [8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8],
        [8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8],
    ]
"""


def test_run_tests_multiple_wrong_answer(python_path, puzzle_8dab14c2):
    result = run_tests(_WRONG_CODE, puzzle_8dab14c2["test"], python_path)
    assert result["status"] == "wrong_answer"
    assert result["total"] == 4
    assert result["passed"] == 0
    assert result["correct"] is False


def test_run_tests_multiple_error(python_path, puzzle_8dab14c2):
    result = run_tests(_ERROR_CODE, puzzle_8dab14c2["test"], python_path)
    assert result["status"] == "error_exec"
    assert result["total"] == 4


def test_run_tests_multiple_partial(python_path, puzzle_8dab14c2):
    result = run_tests(_PARTIAL_8DAB14C2, puzzle_8dab14c2["test"], python_path)
    assert result["status"] == "wrong_answer"
    assert result["total"] == 4
    assert result["passed"] == 1
    assert result["correct"] is False
    assert result["details"][0]["correct"] is True
    assert result["details"][0]["cell_accuracy"] == 1.0
    for detail in result["details"][1:]:
        assert detail["correct"] is False
