def transform(grid):

    if not grid:
        return []

    h = len(grid)
    w = len(grid[0])

    result = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(h):
        for c in range(w):
            if not visited[r][c] and grid[r][c] == 2:

                component = []
                stack = [(r, c)]
                visited[r][c] = True

                while stack:
                    x, y = stack.pop()
                    component.append((x, y))

                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w:
                            if not visited[nx][ny] and grid[nx][ny] == 2:
                                visited[nx][ny] = True
                                stack.append((nx, ny))

                if len(component) >= 4:
                    for x, y in component:
                        result[x][y] = 6

    return result