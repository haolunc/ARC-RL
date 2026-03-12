def transform(grid):

    h = len(grid)
    w = len(grid[0])

    result = [row[:] for row in grid]

    for r in range(h):
        for c in range(w):
            v = grid[r][c]

            if v == 7 or v == 4:
                continue
            r2 = h - 1 - r
            c2 = w - 1 - c

            result[r2][c2] = v

    return result