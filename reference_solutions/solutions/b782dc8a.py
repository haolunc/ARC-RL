import collections
from copy import deepcopy
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    if not grid:
        return []

    h, w = len(grid), len(grid[0])
    out = deepcopy(grid)

    seed_colors = {v for row in grid for v in row if v != 0 and v != 8}
    if len(seed_colors) != 2:

        return out
    c1, c2 = tuple(seed_colors)

    q = collections.deque()
    for i in range(h):
        for j in range(w):
            if grid[i][j] in (c1, c2):
                q.append((i, j))

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while q:
        i, j = q.popleft()
        cur = out[i][j]
        opp = c1 if cur == c2 else c2   
        for di, dj in dirs:
            ni, nj = i + di, j + dj
            if 0 <= ni < h and 0 <= nj < w and out[ni][nj] == 0:
                out[ni][nj] = opp
                q.append((ni, nj))

    return out