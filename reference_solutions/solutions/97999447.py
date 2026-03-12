def transform(grid):

    out = [row[:] for row in grid]

    for r_idx, row in enumerate(out):
        start_col = None
        colour = None

        for c_idx, val in enumerate(row):
            if val != 0:
                start_col = c_idx
                colour = val
                break

        if start_col is not None:
            for j in range(start_col, len(row)):
                out[r_idx][j] = colour if (j - start_col) % 2 == 0 else 5

    return out