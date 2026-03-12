from collections import deque
from typing import List

def transform(grid: List[List[int]]) -> List[List[int]]:

    freq = {}
    for row in grid:
        for v in row:
            freq[v] = freq.get(v, 0) + 1
    background = max(freq.items(), key=lambda kv: kv[1])[0]

    n = len(grid)
    m = len(grid[0])
    visited = [[False] * m for _ in range(n)]

    components = []

    def bfs(sr: int, sc: int, colour: int) -> None:
        q = deque()
        q.append((sr, sc))
        visited[sr][sc] = True
        while q:
            r, c = q.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < m:
                    if not visited[nr][nc] and grid[nr][nc] == colour:
                        visited[nr][nc] = True
                        q.append((nr, nc))

    for i in range(n):
        for j in range(m):
            if not visited[i][j] and grid[i][j] != background:
                colour = grid[i][j]
                bfs(i, j, colour)
                components.append(colour)

    components.sort(reverse=True)

    out_vals = components[:6] + [0] * (6 - len(components))

    result = [out_vals[0:3], out_vals[3:6]]
    return result