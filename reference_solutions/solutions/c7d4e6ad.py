def transform(grid):

    out = [row[:] for row in grid]

    for i, row in enumerate(out):

        colour = None
        for val in row:
            if val != 0:
                colour = val
                break

        if colour is not None:

            for j, val in enumerate(row):
                if val == 5:
                    out[i][j] = colour

    return out