def transform(grid):

    out = [row[:] for row in grid]

    h = len(grid)
    if h == 0:
        return out
    w = len(grid[0])

    for r in range(h - 2):          
        for c in range(w):
            if grid[r][c] == 1 and grid[r + 1][c] == 5:
                out[r][c] = 0          
                out[r + 2][c] = 1      

    return out