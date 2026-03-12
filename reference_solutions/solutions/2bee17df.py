def transform(grid):

    h = len(grid)
    w = len(grid[0])

    out = [row[:] for row in grid]

    for i in range(1, h - 1):

        if all(grid[i][j] == 0 for j in range(1, w - 1)):
            for j in range(1, w - 1):
                out[i][j] = 3

    for j in range(1, w - 1):
        if all(grid[i][j] == 0 for i in range(1, h - 1)):
            for i in range(1, h - 1):
                out[i][j] = 3

    return out