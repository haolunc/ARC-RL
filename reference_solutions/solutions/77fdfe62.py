def transform(grid):

    N = len(grid)
    M = len(grid[0])

    TL = grid[0][0]
    TR = grid[0][M - 1]
    BL = grid[N - 1][0]
    BR = grid[N - 1][M - 1]

    inner = [row[2:M - 2] for row in grid[2:N - 2]]

    h = len(inner)          
    w = len(inner[0])       

    out = [[0] * w for _ in range(h)]

    half_h = h // 2
    half_w = w // 2

    for i in range(h):
        for j in range(w):
            v = inner[i][j]
            if v == 0:
                out[i][j] = 0
            else:  
                if j < half_w:          
                    out[i][j] = TL if i < half_h else BL
                else:                   
                    out[i][j] = TR if i < half_h else BR
    return out