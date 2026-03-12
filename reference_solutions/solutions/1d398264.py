def transform(grid):

    import copy

    h = len(grid)
    w = len(grid[0])

    cells = [(r, c, grid[r][c]) for r in range(h) for c in range(w) if grid[r][c] != 0]

    if not cells:                
        return copy.deepcopy(grid)

    rows = sorted(r for r, _, _ in cells)
    cols = sorted(c for _, c, _ in cells)
    median_row = rows[len(rows) // 2]
    median_col = cols[len(cols) // 2]

    def sgn(x):
        return (x > 0) - (x < 0)

    out = [list(row) for row in grid]

    for r, c, val in cells:
        dr = sgn(r - median_row)
        dc = sgn(c - median_col)

        if dr == 0 and dc == 0:
            continue

        rr, cc = r, c
        while 0 <= rr < h and 0 <= cc < w:
            out[rr][cc] = val
            rr += dr
            cc += dc

    return out