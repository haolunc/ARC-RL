def transform(grid):

    if not grid:
        return []

    h, w = len(grid), len(grid[0])

    out = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for i in range(h):
        for j in range(w):
            if visited[i][j] or grid[i][j] == 0:
                visited[i][j] = True
                continue

            stack = [(i, j)]
            comp = []
            visited[i][j] = True
            colour = grid[i][j]

            while stack:
                x, y = stack.pop()
                comp.append((x, y))
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w:
                        if not visited[nx][ny] and grid[nx][ny] == colour:
                            visited[nx][ny] = True
                            stack.append((nx, ny))

            if len(comp) < 3:
                for x, y in comp:
                    out[x][y] = 3  

    return out