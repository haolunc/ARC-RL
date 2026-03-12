from collections import Counter
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:
    n = len(grid)                     

    uniform_row = -1
    uniform_colour = None
    for i, row in enumerate(grid):
        if len(set(row)) == 1:        
            uniform_row = i
            uniform_colour = row[0]
            break

    uniform_col = -1
    for j in range(n):
        col_vals = {grid[i][j] for i in range(n)}
        if len(col_vals) == 1:        
            uniform_col = j
            break

    def most_common(r0: int, r1: int, c0: int, c1: int) -> int:

        cnt = Counter()
        for r in range(r0, r1):
            for c in range(c0, c1):
                cnt[grid[r][c]] += 1

        most, _ = min(cnt.items(), key=lambda kv: (-kv[1], kv[0]))
        return most

    TL = most_common(0, uniform_row, 0, uniform_col)
    TR = most_common(0, uniform_row, uniform_col + 1, n)
    BL = most_common(uniform_row + 1, n, 0, uniform_col)
    BR = most_common(uniform_row + 1, n, uniform_col + 1, n)

    v = uniform_colour

    return [
        [TL, v, TR],
        [v,  v, v ],
        [BL, v, BR]
    ]