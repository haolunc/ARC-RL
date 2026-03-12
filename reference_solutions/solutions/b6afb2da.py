def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if not visited[r][c] and grid[r][c] == 5:

                component = []
                stack = [(r, c)]
                visited[r][c] = True

                while stack:
                    x, y = stack.pop()
                    component.append((x, y))

                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w:
                            if not visited[nx][ny] and grid[nx][ny] == 5:
                                visited[nx][ny] = True
                                stack.append((nx, ny))

                rows = [p[0] for p in component]
                cols = [p[1] for p in component]
                min_r, max_r = min(rows), max(rows)
                min_c, max_c = min(cols), max(cols)

                for i in range(min_r, max_r + 1):
                    for j in range(min_c, max_c + 1):
                        if (i == min_r or i == max_r) and (j == min_c or j == max_c):
                            out[i][j] = 1          
                        elif i == min_r or i == max_r or j == min_c or j == max_c:
                            out[i][j] = 4          
                        else:
                            out[i][j] = 2          

    return out