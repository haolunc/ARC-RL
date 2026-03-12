import collections
from copy import deepcopy
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    h = len(grid)
    w = len(grid[0]) if h else 0

    flat = [c for row in grid for c in row]
    freq = collections.Counter(flat)

    background = max(freq, key=freq.get)

    other = [c for c in freq if c != background]
    if len(other) == 0:
        return deepcopy(grid)          

    primary = max(other, key=lambda c: freq[c])
    filler = None
    if len(other) > 1:
        filler = [c for c in other if c != primary][0]

    if filler is None:
        return deepcopy(grid)

    filler_left = freq[filler]

    out = [row[:] for row in grid]
    for i in range(h):
        for j in range(w):
            if out[i][j] == filler:
                out[i][j] = background

    for i in range(h):

        cols = [j for j, val in enumerate(grid[i]) if val == primary]
        if len(cols) == 2:
            left, right = cols
            for j in range(left + 1, right):
                if filler_left == 0:
                    break
                if out[i][j] == background:
                    out[i][j] = filler
                    filler_left -= 1
        if filler_left == 0:
            break

    return out