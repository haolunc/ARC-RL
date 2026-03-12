# Reference Solutions Summary

Source: [Trelis/arc-agi-2-reasoning-5](https://huggingface.co/datasets/Trelis/arc-agi-2-reasoning-5) (Apache 2.0)

Downloaded: 2026-03-11

## Overview

- **Total solutions**: 651 unique tasks
- Each file is a `def transform(input_grid)` Python function, verified correct on both train and test examples
- Per task, the shortest correct solution was selected

## Coverage by Subset

| Subset              | Solutions | Total Tasks | Coverage |
|---------------------|-----------|-------------|----------|
| ARC-AGI-1 training  | 323       | 400         | 80.8%    |
| ARC-AGI-1 evaluation| 243       | 400         | 60.8%    |
| ARC-AGI-2 training  | 648       | 1000        | 64.8%    |
| ARC-AGI-2 evaluation| 0         | 120         | 0.0%     |

Note: ARC-AGI-1 tasks are a subset of ARC-AGI-2 (773 tasks overlap), so most solutions appear in both.

## Breakdown by Version

| Category                    | Count |
|-----------------------------|-------|
| Exclusive to ARC-AGI-1      | 3     |
| Exclusive to ARC-AGI-2      | 85    |
| In both ARC-AGI-1 & 2       | 563   |

## File Format

Each `solutions/{task_id}.py` contains a standalone Python function:

```python
def transform(input_grid):
    # ... transformation logic ...
    return output_grid
```

- Input: `list[list[int]]` (grid of 0-9)
- Output: `list[list[int]]`
- May use numpy (imported by the eval driver)
- May use Python standard library
