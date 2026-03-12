def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    out = [[5 for _ in range(w)] for _ in range(h)]

    for i in range(h):
        for j in range(w - 1):          
            val = grid[i][j + 1]
            if val != 0:                
                out[i][j] = val

    return out