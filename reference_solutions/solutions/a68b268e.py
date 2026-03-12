def transform(grid):

    n = len(grid)            
    center = n // 2          
    size = center            

    out = [[0] * size for _ in range(size)]

    for i in range(size):
        for j in range(size):

            tl = grid[i][j]
            tr = grid[i][center + 1 + j]
            bl = grid[center + 1 + i][j]
            br = grid[center + 1 + i][center + 1 + j]

            for val in (tl, tr, bl, br):
                if val != 0:
                    out[i][j] = val
                    break

    return out