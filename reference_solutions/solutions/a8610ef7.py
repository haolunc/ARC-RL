def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0
    out = [[0] * w for _ in range(h)]

    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val == 0:
                out[r][c] = 0
            else:  
                mirrored_val = grid[h - 1 - r][c]
                out[r][c] = 2 if mirrored_val == 8 else 5
    return out