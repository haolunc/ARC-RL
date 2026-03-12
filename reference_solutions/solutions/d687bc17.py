def transform(grid):

    h = len(grid)
    w = len(grid[0])

    top = grid[0][1]          
    bottom = grid[h - 1][1]   
    left = grid[1][0]         
    right = grid[1][w - 1]    

    out = [row[:] for row in grid]

    for i in range(1, h - 1):
        for j in range(1, w - 1):
            v = grid[i][j]
            if v == 0:
                continue
            if v == top:
                out[i][j] = 0
                out[1][j] = v
            elif v == bottom:
                out[i][j] = 0
                out[h - 2][j] = v
            elif v == left:
                out[i][j] = 0
                out[i][1] = v
            elif v == right:
                out[i][j] = 0
                out[i][w - 2] = v
            else:
                out[i][j] = 0   
    return out