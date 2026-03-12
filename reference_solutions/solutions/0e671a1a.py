def transform(grid):

    out = [row[:] for row in grid]

    r4 = c4 = r3 = c3 = r2 = c2 = None
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v == 4:
                r4, c4 = r, c
            elif v == 3:
                r3, c3 = r, c
            elif v == 2:
                r2, c2 = r, c

    if None in (r4, c4, r3, c3, r2, c2):
        return out   

    def draw_horiz(row, c_start, c_end):
        lo, hi = (c_start, c_end) if c_start <= c_end else (c_end, c_start)
        for c in range(lo, hi + 1):
            if out[row][c] == 0:
                out[row][c] = 5

    def draw_vert(col, r_start, r_end):
        lo, hi = (r_start, r_end) if r_start <= r_end else (r_end, r_start)
        for r in range(lo, hi + 1):
            if out[r][col] == 0:
                out[r][col] = 5

    draw_horiz(r4, c4, c3)

    draw_vert(c3, r4, r3)

    draw_vert(c4, r4, r2)

    draw_horiz(r2, c4, c2)

    return out