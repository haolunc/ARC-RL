def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    filler = {2: 1, 3: 6, 8: 4}

    out = [[0 for _ in range(w)] for _ in range(h)]

    for i in range(h):
        for j in range(w):
            c = grid[i][j]
            if c == 0:
                continue
            f = filler.get(c, c)          
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < h and 0 <= nj < w:
                        if di == 0 and dj == 0:
                            out[ni][nj] = c          
                        else:
                            out[ni][nj] = f          
    return out