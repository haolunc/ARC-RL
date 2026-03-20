"""Tests for arc.eval.test — code extraction and grid comparison."""

from arc.eval.test import extract_code, compare_grids


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
