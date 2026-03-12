def transform(grid):

    transformed = []
    for row in grid:

        if len(set(row)) == 1:
            transformed.append([5] * len(row))
        else:
            transformed.append([0] * len(row))
    return transformed