from collections import Counter
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    if not grid or not grid[0]:
        return grid  

    width = len(grid[0])
    central_col = width // 2  

    first_row = grid[0]
    counts = Counter(first_row)

    max_freq = max(counts.values())

    chosen_value = None
    for val in first_row:
        if counts[val] == max_freq:
            chosen_value = val
            break

    new_grid = [row[:] for row in grid]

    bottom_row_index = len(grid) - 1
    new_grid[bottom_row_index][central_col] = chosen_value

    return new_grid