def transform(grid):

    result = [row[:] for row in grid]

    for i, row in enumerate(grid):

        D = None
        for v in row:
            if v != 0 and v != 5:
                D = v
                break

        if D is not None:
            result[i] = [D if v == 5 else v for v in row]

    return result