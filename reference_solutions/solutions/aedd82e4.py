def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    for i in range(h):
        for j in range(w):
            if grid[i][j] != 2:
                continue

            isolated = True
            if i > 0   and grid[i-1][j] == 2: isolated = False
            if i < h-1 and grid[i+1][j] == 2: isolated = False
            if j > 0   and grid[i][j-1] == 2: isolated = False
            if j < w-1 and grid[i][j+1] == 2: isolated = False

            if isolated:
                out[i][j] = 1

    return out