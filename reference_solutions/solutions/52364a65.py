def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    min_col = {}
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v == 8:
                continue
            if v not in min_col or c < min_col[v]:
                min_col[v] = c

    out = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v == 8:
                out[r][c] = 8
                continue

            if c < min_col[v] + 2:
                out[r][c] = 8
            else:
                out[r][c] = v
    return out