def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 2 or visited[r][c]:
                continue

            stack = [(r, c)]
            visited[r][c] = True
            component = [(r, c)]

            while stack:
                x, y = stack.pop()
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w:
                        if not visited[nx][ny] and grid[nx][ny] == 2:
                            visited[nx][ny] = True
                            stack.append((nx, ny))
                            component.append((nx, ny))

            rows = [p[0] for p in component]
            cols = [p[1] for p in component]
            rmin, rmax = min(rows), max(rows)
            cmin, cmax = min(cols), max(cols)

            interior_h = rmax - rmin - 1
            interior_w = cmax - cmin - 1
            has_interior = interior_h > 0 and interior_w > 0

            border_cells = 2 * (rmax - rmin + 1) + 2 * (cmax - cmin + 1) - 4
            is_border = has_interior and (len(component) == border_cells)

            if is_border:
                for i in range(rmin + 1, rmax):
                    for j in range(cmin + 1, cmax):
                        out[i][j] = 3

            for i, j in component:
                out[i][j] = 0

    return out