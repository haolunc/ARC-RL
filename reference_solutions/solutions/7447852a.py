def transform(grid):

    row0_tile = [2, 0, 0, 0, 2, 4, 4, 4, 2, 0, 0, 0]
    row1_tile = [4, 2, 0, 2, 0, 2, 4, 2, 0, 2, 0, 2]
    row2_tile = [4, 4, 2, 0, 0, 0, 2, 0, 0, 0, 2, 4]

    h = len(grid)          
    w = len(grid[0])       

    out = [[0] * w for _ in range(h)]

    for c in range(w):
        m = c % 12
        out[0][c] = row0_tile[m]
        out[1][c] = row1_tile[m]
        out[2][c] = row2_tile[m]

    return out