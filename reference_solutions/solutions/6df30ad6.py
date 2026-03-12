import math
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    h = len(grid)
    w = len(grid[0]) if h else 0

    five_cells = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 5]
    if not five_cells:                     
        return [[0] * w for _ in range(h)]

    rc = sum(r for r, _ in five_cells) / len(five_cells)
    cc = sum(c for _, c in five_cells) / len(five_cells)

    best_dist = float('inf')
    best_colour = 0
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val != 0 and val != 5:
                d = math.hypot(r - rc, c - cc)
                if d < best_dist:
                    best_dist = d
                    best_colour = val

    out = [[0] * w for _ in range(h)]
    for r, c in five_cells:
        out[r][c] = best_colour

    return out