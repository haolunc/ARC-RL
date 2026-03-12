def transform(grid):

    from collections import deque

    h = len(grid)
    w = len(grid[0]) if h else 0

    g = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for i in range(h):
        for j in range(w):
            if not visited[i][j] and g[i][j] == 5:

                q = deque()
                q.append((i, j))
                visited[i][j] = True
                component = [(i, j)]

                while q:
                    r, c = q.popleft()
                    for dr, dc in dirs:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < h and 0 <= nc < w:
                            if not visited[nr][nc] and g[nr][nc] == 5:
                                visited[nr][nc] = True
                                q.append((nr, nc))
                                component.append((nr, nc))

                rows = [p[0] for p in component]
                cols = [p[1] for p in component]
                rmin, rmax = min(rows), max(rows)
                cmin, cmax = min(cols), max(cols)

                interior_rows = rmax - rmin - 1
                interior_cols = cmax - cmin - 1

                if interior_rows <= 0 or interior_cols <= 0:
                    continue

                k = min(interior_rows, interior_cols)
                fill_colour = 5 + k

                for rr in range(rmin + 1, rmax):
                    for cc in range(cmin + 1, cmax):
                        g[rr][cc] = fill_colour

    return g