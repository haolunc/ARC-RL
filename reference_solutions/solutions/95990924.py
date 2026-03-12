def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    def set_if_zero(r, c, val):
        if 0 <= r < h and 0 <= c < w and out[r][c] == 0:
            out[r][c] = val

    for r in range(h - 1):
        for c in range(w - 1):
            if (grid[r][c] == 5 and grid[r + 1][c] == 5 and
                grid[r][c + 1] == 5 and grid[r + 1][c + 1] == 5):

                set_if_zero(r - 1, c - 1, 1)   
                set_if_zero(r - 1, c + 2, 2)   
                set_if_zero(r + 2, c - 1, 3)   
                set_if_zero(r + 2, c + 2, 4)   

    return out