def transform(grid):

    h = len(grid)          
    w = len(grid[0])       
    band = h // 3          

    out = [[0] * w for _ in range(band)]

    for r in range(band):
        for c in range(w):

            for src in (r + 2 * band, r, r + band):
                val = grid[src][c]
                if val != 0:
                    out[r][c] = val
                    break
            else:
                out[r][c] = 0
    return out