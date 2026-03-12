def transform(grid):

    colours = set()
    for row in grid:
        colours.update(row)

    if len(colours) != 2 or 5 not in colours:

        other = None
    else:

        other = (colours - {5}).pop()

    out = []
    for row in grid:
        out_row = []
        for val in row:
            if val == 5:
                out_row.append(other)
            else:
                out_row.append(0)
        out.append(out_row)

    return out