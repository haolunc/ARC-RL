def transform(grid):

    h = len(grid)
    w = len(grid[0])

    a = grid[0][0]
    b = grid[0][1]
    c = grid[1][0]
    d = grid[1][1]

    swap = {a: b, b: a, c: d, d: c}

    out = [row[:] for row in grid]

    for i in range(h):
        for j in range(w):

            if i < 2 and j < 2:
                continue
            val = grid[i][j]
            if val in swap:
                out[i][j] = swap[val]

    return out