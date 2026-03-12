def transform(grid):

    if not grid:
        return []

    rows = len(grid)
    cols = len(grid[0])

    rows_with_8 = set()
    cols_with_8 = set()

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 8:
                rows_with_8.add(r)
                cols_with_8.add(c)

    out = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and r in rows_with_8 and c in cols_with_8:
                out[r][c] = 2

    return out