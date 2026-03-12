from collections import deque
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    if not grid:
        return []

    h, w = len(grid), len(grid[0])
    visited = [[False] * w for _ in range(h)]
    q = deque()

    for i in range(h):
        for j in range(w):
            if i == 0 or i == h - 1 or j == 0 or j == w - 1:
                if grid[i][j] == 0:
                    visited[i][j] = True
                    q.append((i, j))

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while q:
        i, j = q.popleft()
        for di, dj in dirs:
            ni, nj = i + di, j + dj
            if 0 <= ni < h and 0 <= nj < w:
                if not visited[ni][nj] and grid[ni][nj] == 0:
                    visited[ni][nj] = True
                    q.append((ni, nj))

    result = [row[:] for row in grid]   
    for i in range(h):
        for j in range(w):
            if grid[i][j] == 0 and not visited[i][j]:
                result[i][j] = 4

    return result