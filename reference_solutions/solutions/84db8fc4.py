from collections import deque

def transform(grid):
    if not grid:
        return grid

    n = len(grid)
    m = len(grid[0])

    res = [row[:] for row in grid]
    visited = [[False] * m for _ in range(n)]
    q = deque()

    def try_enqueue(i, j):
        if 0 <= i < n and 0 <= j < m and grid[i][j] == 0 and not visited[i][j]:
            visited[i][j] = True
            res[i][j] = 2
            q.append((i, j))

    for i in range(n):
        try_enqueue(i, 0)
        try_enqueue(i, m - 1)
    for j in range(m):
        try_enqueue(0, j)
        try_enqueue(n - 1, j)

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while q:
        x, y = q.popleft()
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m and not visited[nx][ny] and grid[nx][ny] == 0:
                visited[nx][ny] = True
                res[nx][ny] = 2
                q.append((nx, ny))

    for i in range(n):
        for j in range(m):
            if grid[i][j] == 0 and res[i][j] != 2:
                res[i][j] = 5

    return res