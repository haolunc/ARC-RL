def transform(grid):

    pos3 = pos4 = None
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == 3:
                pos3 = (r, c)
            elif val == 4:
                pos4 = (r, c)

    if pos3 is None or pos4 is None:
        return [list(row) for row in grid]

    r3, c3 = pos3
    r4, c4 = pos4

    def sgn(x):
        return (x > 0) - (x < 0)

    new_r3 = r3 + sgn(r4 - r3)
    new_c3 = c3 + sgn(c4 - c3)

    out = [list(row) for row in grid]

    out[r3][c3] = 0

    out[new_r3][new_c3] = 3

    return out