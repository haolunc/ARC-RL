def transform(grid: list[list[int]]) -> list[list[int]]:

    if not grid:
        return []

    width = len(grid[0])

    out = [row[:] for row in grid]

    for r, row in enumerate(out):
        for c, val in enumerate(row):
            if val == 5 and (c % 2) != (width % 2):
                out[r][c] = 3
    return out