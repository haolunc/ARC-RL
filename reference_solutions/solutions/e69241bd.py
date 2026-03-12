from collections import deque
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for i in range(h):
        for j in range(w):
            seed = grid[i][j]
            if seed != 0 and seed != 5:

                q = deque()
                q.append((i, j))

                while q:
                    x, y = q.popleft()
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w:

                            if out[nx][ny] == 0:
                                out[nx][ny] = seed
                                q.append((nx, ny))

    return out