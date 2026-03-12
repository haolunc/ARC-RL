def transform(grid):

    transformed = []
    for row in grid:

        rev = list(reversed(row))

        new_row = row + rev
        transformed.append(new_row)
    return transformed