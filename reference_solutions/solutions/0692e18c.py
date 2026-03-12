def transform(grid):

    n = len(grid)                     
    out_size = n * 3

    out = [[0 for _ in range(out_size)] for _ in range(out_size)]

    for i in range(n):
        for j in range(n):
            v = grid[i][j]
            if v == 0:
                continue               

            for r in range(3):
                for c in range(3):
                    if grid[r][c] == 0:
                        out[i * 3 + r][j * 3 + c] = v

    return out