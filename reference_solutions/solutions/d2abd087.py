def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 5 and not visited[r][c]:

                stack = [(r, c)]
                visited[r][c] = True
                component = []

                while stack:
                    x, y = stack.pop()
                    component.append((x, y))

                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w:
                            if not visited[nx][ny] and grid[nx][ny] == 5:
                                visited[nx][ny] = True
                                stack.append((nx, ny))

                new_colour = 2 if len(component) == 6 else 1
                for x, y in component:
                    out[x][y] = new_colour

    return out