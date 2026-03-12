def transform(grid):

    out = [row[:] for row in grid]

    colour_positions = {}
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val != 0:
                colour_positions.setdefault(val, []).append((r, c))

    for colour, pos in colour_positions.items():
        if len(pos) != 2:
            continue          
        (r1, c1), (r2, c2) = pos

        step_r = 1 if r2 > r1 else -1
        step_c = 1 if c2 > c1 else -1

        r, c = r1, c1
        while True:
            out[r][c] = colour          
            if (r, c) == (r2, c2):
                break
            r += step_r
            c += step_c

    return out