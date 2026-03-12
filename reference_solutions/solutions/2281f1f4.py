def transform(grid):

    h = len(grid)
    w = len(grid[0])

    pattern_cols = [c for c in range(w) if grid[0][c] == 5]

    out = [row[:] for row in grid]

    for r in range(1, h):
        if grid[r][w - 1] == 5:          
            for c in pattern_cols:
                out[r][c] = 2            

    return out