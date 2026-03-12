import copy
from typing import List, Tuple

def transform(grid: List[List[int]]) -> List[List[int]]:
    h = set()

    colours = set()
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v != 0:
                colours.add(v)
    if len(colours) != 2:

        return grid

    boxes = {}
    for col in colours:
        min_r, max_r = len(grid), -1
        min_c, max_c = len(grid[0]), -1
        for r, row in enumerate(grid):
            for c, v in enumerate(row):
                if v == col:
                    min_r = min(min_r, r)
                    max_r = max(max_r, r)
                    min_c = min(min_c, c)
                    max_c = max(max_c, c)
        boxes[col] = (min_r, max_r, min_c, max_c)

    (r1a, r2a, c1a, c2a), (r1b, r2b, c1b, c2b) = boxes.values()

    def fill_range(a1, a2, b1, b2) -> Tuple[int, int]:

        if a2 < b1 - 1:               
            return a2 + 1, b1
        if b2 < a1 - 1:               
            return b2 + 1, a1

        inter_start = max(a1, b1)
        inter_end   = min(a2, b2)     

        if inter_end - inter_start <= 1:
            return 0, 0               
        return inter_start + 1, inter_end

    row_start, row_end = fill_range(r1a, r2a, r1b, r2b)   
    col_start, col_end = fill_range(c1a, c2a, c1b, c2b)

    out = copy.deepcopy(grid)
    for r in range(row_start, row_end):
        for c in range(col_start, col_end):
            out[r][c] = 8
    return out