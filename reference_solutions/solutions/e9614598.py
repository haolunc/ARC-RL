def transform(grid):

    out = [row[:] for row in grid]

    blues = [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == 1]

    if len(blues) != 2:
        return out

    (r1, c1), (r2, c2) = blues

    mr = (r1 + r2) // 2
    mc = (c1 + c2) // 2

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    def set_green(r, c):
        if 0 <= r < rows and 0 <= c < cols:
            out[r][c] = 3

    set_green(mr, mc)

    set_green(mr - 1, mc)   
    set_green(mr + 1, mc)   
    set_green(mr, mc - 1)   
    set_green(mr, mc + 1)   

    return out