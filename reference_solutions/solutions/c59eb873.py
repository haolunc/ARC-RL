def transform(grid):

    out = []
    for row in grid:

        new_row = []
        for val in row:
            new_row.extend([val, val])

        out.append(new_row)
        out.append(new_row.copy())
    return out