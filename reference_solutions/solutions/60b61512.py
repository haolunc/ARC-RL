def transform(grid):

    g = [row[:] for row in grid]
    h = len(g)
    w = len(g[0]) if h else 0

    visited = [[False] * w for _ in range(h)]

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1),  (1, 0), (1, 1)]

    for r in range(h):
        for c in range(w):
            if g[r][c] != 4 or visited[r][c]:
                continue

            stack = [(r, c)]
            component = []
            visited[r][c] = True

            while stack:
                y, x = stack.pop()
                component.append((y, x))
                for dy, dx in dirs:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        if not visited[ny][nx] and g[ny][nx] == 4:
                            visited[ny][nx] = True
                            stack.append((ny, nx))

            rows = [y for y, _ in component]
            cols = [x for _, x in component]
            rmin, rmax = min(rows), max(rows)
            cmin, cmax = min(cols), max(cols)

            if rmax - rmin == 2 and cmax - cmin == 2:
                for yy in range(rmin, rmax + 1):
                    for xx in range(cmin, cmax + 1):
                        if g[yy][xx] == 0:
                            g[yy][xx] = 7

    return g