def transform(grid):
    from collections import deque

    if not grid:
        return grid
    n = len(grid)
    m = len(grid[0])

    visited = [[False]*m for _ in range(n)]
    res = [row[:] for row in grid]

    for i in range(n):
        for j in range(m):
            if grid[i][j] == 5 and not visited[i][j]:

                q = deque()
                q.append((i, j))
                visited[i][j] = True
                comp = []
                while q:
                    x, y = q.popleft()
                    comp.append((x, y))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < n and 0 <= ny < m:
                            if not visited[nx][ny] and grid[nx][ny] == 5:
                                visited[nx][ny] = True
                                q.append((nx, ny))
                s = len(comp)
                color = 5 - s
                for x, y in comp:
                    res[x][y] = color

    return res