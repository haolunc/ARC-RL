def transform(grid):

    from collections import deque
    n = len(grid)
    m = len(grid[0])

    six = {(i, j) for i in range(n) for j in range(m) if grid[i][j] == 6}

    external = [[False] * m for _ in range(n)]
    q = deque()

    for i in range(n):
        for j in range(m):
            if (i == 0 or i == n - 1 or j == 0 or j == m - 1) and grid[i][j] == 8:
                external[i][j] = True
                q.append((i, j))

    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while q:
        x, y = q.popleft()
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m and not external[nx][ny] and grid[nx][ny] == 8:
                external[nx][ny] = True
                q.append((nx, ny))

    out = [row[:] for row in grid]          
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 8 and not external[i][j]:
                out[i][j] = 4                

    dirs8 = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),          (0, 1),
             (1, -1),  (1, 0), (1, 1)]

    for i in range(n):
        for j in range(m):

            if grid[i][j] == 8 and out[i][j] == 8:
                for dx, dy in dirs8:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < n and 0 <= nj < m and (ni, nj) in six:
                        out[i][j] = 3
                        break

    return out