def transform(grid):

    if not grid:
        return []

    h = len(grid)
    w = len(grid[0])
    out = []

    for row in grid:

        p = 0
        while p < w and row[p] != 0:
            p += 1

        prefix = row[:p]

        repeat = w - 2 * p + 1

        new_row = (
            prefix +
            [prefix[0]] * repeat +
            prefix[1:]
        )
        out.append(new_row)

    return out