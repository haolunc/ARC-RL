def transform(grid):

    h = len(grid)
    w = len(grid[0])

    r = c = None
    v = 0
    for i in range(h):
        for j in range(w):
            if grid[i][j] != 0:
                r, c = i, j
                v = grid[i][j]
                break
        if r is not None:
            break

    if r is None:
        return [row[:] for row in grid]

    out = [row[:] for row in grid]

    for i in range(r + 1):
        for j in range(w):
            out[i][j] = 4 if ((j - c) % 2 == 0) else 0

    if r + 1 < h:
        out[r + 1][c] = v
    else:

        out[r][c] = v

    return out