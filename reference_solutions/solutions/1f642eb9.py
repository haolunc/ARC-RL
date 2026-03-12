def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H > 0 else 0
    res = [row[:] for row in grid]

    coords = [(r, c) for r in range(H) for c in range(W) if grid[r][c] == 8]
    if not coords:
        return res  

    tr = min(r for r, _ in coords)
    br = max(r for r, _ in coords)
    lc = min(c for _, c in coords)
    rc = max(c for _, c in coords)

    for c in range(lc, rc + 1):
        v = grid[0][c]
        if v != 0:
            res[tr][c] = v

    for r in range(tr, br + 1):
        v = grid[r][0]
        if v != 0:
            res[r][lc] = v

    for c in range(lc, rc + 1):
        v = grid[H - 1][c]
        if v != 0:
            res[br][c] = v

    for r in range(tr, br + 1):
        v = grid[r][W - 1]
        if v != 0:
            res[r][rc] = v

    return res