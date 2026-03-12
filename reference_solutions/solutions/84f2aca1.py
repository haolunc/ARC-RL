from collections import deque
from copy import deepcopy
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    if not grid:
        return []

    h, w = len(grid), len(grid[0])
    out = deepcopy(grid)

    visited = [[False] * w for _ in range(h)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 0 or visited[r][c]:
                continue

            q = deque()
            q.append((r, c))
            region = []                
            touches_border = False

            while q:
                x, y = q.popleft()
                if visited[x][y]:
                    continue
                visited[x][y] = True
                region.append((x, y))

                if x == 0 or x == h - 1 or y == 0 or y == w - 1:
                    touches_border = True

                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w:
                        if grid[nx][ny] == 0 and not visited[nx][ny]:
                            q.append((nx, ny))

            if touches_border:

                continue

            fill = 5 if len(region) == 1 else 7
            for x, y in region:
                out[x][y] = fill

    return out