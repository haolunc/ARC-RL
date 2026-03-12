from collections import deque
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:
    h = len(grid)
    w = len(grid[0]) if h else 0

    visited = [[False] * w for _ in range(h)]
    q = deque()

    for y in range(h):
        for x in (0, w - 1):
            if grid[y][x] == 0 and not visited[y][x]:
                visited[y][x] = True
                q.append((y, x))
    for x in range(w):
        for y in (0, h - 1):
            if grid[y][x] == 0 and not visited[y][x]:
                visited[y][x] = True
                q.append((y, x))

    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    while q:
        y, x = q.popleft()
        for dy, dx in dirs:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                if grid[ny][nx] == 0 and not visited[ny][nx]:
                    visited[ny][nx] = True
                    q.append((ny, nx))

    result = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            val = grid[y][x]
            if val == 0:
                result[y][x] = 3 if visited[y][x] else 2
            else:
                result[y][x] = val
    return result