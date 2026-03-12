def transform(grid):

    out = [[0] * 5 for _ in range(5)]
    for i in range(5):
        for j in range(5):

            tr = grid[i][j + 5]       
            bl = grid[i + 5][j]       
            br = grid[i + 5][j + 5]   
            tl = grid[i][j]           
            for val in (tr, bl, br, tl):
                if val != 0:
                    out[i][j] = val
                    break

    return out