def transform(grid):

    h = len(grid)
    w = len(grid[0])
    visited = [[False] * w for _ in range(h)]
    components = []

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for i in range(h):
        for j in range(w):
            if grid[i][j] == 5 and not visited[i][j]:

                stack = [(i, j)]
                visited[i][j] = True
                comp = []
                while stack:
                    x, y = stack.pop()
                    comp.append((x, y))
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w:
                            if not visited[nx][ny] and grid[nx][ny] == 5:
                                visited[nx][ny] = True
                                stack.append((nx, ny))
                components.append(comp)

    components.sort(key=len, reverse=True)

    colour_order = [1, 4, 2]

    new_grid = [row[:] for row in grid]

    for idx, comp in enumerate(components):
        if idx >= len(colour_order):
            break
        col = colour_order[idx]
        for x, y in comp:
            new_grid[x][y] = col

    return new_grid