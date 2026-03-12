def transform(grid):

    h = len(grid)
    if h == 0:
        return []
    w = len(grid[0])

    out = [row[:] for row in grid]

    for i in range(h - 1):          
        j = w - 1 - i               
        out[i][j] = 2

    for j in range(1, w):
        out[h - 1][j] = 4

    return out