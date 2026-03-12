from collections import deque
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:
    h = len(grid)
    w = len(grid[0])

    reds = [(y, x) for y in range(h) for x in range(w) if grid[y][x] == 2]
    if len(reds) != 2:

        return grid
    (y0, x0), (y1, x1) = reds

    INF = 10 ** 9

    def bfs(start_y: int, start_x: int) -> List[List[int]]:
        dist = [[INF] * w for _ in range(h)]
        q = deque()
        dist[start_y][start_x] = 0
        q.append((start_y, start_x))
        while q:
            y, x = q.popleft()
            d = dist[y][x] + 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w:
                    if grid[ny][nx] == 1:          
                        continue
                    if dist[ny][nx] > d:
                        dist[ny][nx] = d
                        q.append((ny, nx))
        return dist

    dist0 = bfs(y0, x0)
    dist1 = bfs(y1, x1)
    shortest = dist0[y1][x1]          

    out = [row[:] for row in grid]   
    for y in range(h):
        for x in range(w):
            val = grid[y][x]
            if val == 1 or val == 2:
                continue                     
            if dist0[y][x] + dist1[y][x] == shortest:
                out[y][x] = 4

    return out