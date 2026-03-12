def transform(grid):

    twos = [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == 2]
    if len(twos) != 2:

        return grid

    (r1, c1), (r2, c2) = twos

    dr = 0 if r2 == r1 else (1 if r2 > r1 else -1)
    dc = 0 if c2 == c1 else (1 if c2 > c1 else -1)

    r, c = r1, c1
    while True:
        val = grid[r][c]
        if val == 0:
            grid[r][c] = 2
        elif val == 1:
            grid[r][c] = 3

        if (r, c) == (r2, c2):
            break
        r += dr
        c += dc

    return grid