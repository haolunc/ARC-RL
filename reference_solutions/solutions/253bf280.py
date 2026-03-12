def transform(grid):

    res = [list(row) for row in grid]
    if not grid:
        return res

    h = len(grid)
    w = len(grid[0])

    for r in range(h):
        cols = [c for c in range(w) if grid[r][c] == 8]
        if len(cols) >= 2:
            cmin, cmax = min(cols), max(cols)
            for cc in range(cmin + 1, cmax):
                res[r][cc] = 3

    for c in range(w):
        rows = [r for r in range(h) if grid[r][c] == 8]
        if len(rows) >= 2:
            rmin, rmax = min(rows), max(rows)
            for rr in range(rmin + 1, rmax):
                res[rr][c] = 3

    return res