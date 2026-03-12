def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    cells = [(r, c, grid[r][c])
             for r in range(h)
             for c in range(w)
             if grid[r][c] != 0]

    if not cells:
        return [row[:] for row in grid]

    (r1, c1, v1), (r2, c2, v2) = cells[0], cells[1]

    dr = abs(r1 - r2)
    dc = abs(c1 - c2)
    period_rows = 2 * dr if dr != 0 else float('inf')
    period_cols = 2 * dc if dc != 0 else float('inf')

    repeat_rows = period_rows <= h

    out = [[0 for _ in range(w)] for _ in range(h)]

    if repeat_rows:                     
        for r, c, val in cells:
            for rr in range(r, h, period_rows):
                out[rr] = [val] * w   
    else:                               
        for r, c, val in cells:
            for cc in range(c, w, period_cols):
                for rr in range(h):
                    out[rr][cc] = val

    return out