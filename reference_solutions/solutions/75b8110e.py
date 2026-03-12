def transform(grid):

    n = len(grid)
    h = n // 2                     

    TL = [row[:h] for row in grid[:h]]
    TR = [row[h:] for row in grid[:h]]
    BL = [row[:h] for row in grid[h:]]
    BR = [row[h:] for row in grid[h:]]

    out = [[0] * h for _ in range(h)]
    for i in range(h):
        for j in range(h):
            for quad in (TR, BL, BR, TL):   
                v = quad[i][j]
                if v != 0:
                    out[i][j] = v
                    break

    return out