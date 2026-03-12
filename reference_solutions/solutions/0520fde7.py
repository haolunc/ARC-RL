def transform(grid):

    out = [[0 for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            if grid[i][j] == 1 and grid[i][j + 4] == 1:
                out[i][j] = 2
            else:
                out[i][j] = 0
    return out