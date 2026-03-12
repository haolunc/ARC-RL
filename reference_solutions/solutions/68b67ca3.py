def transform(grid):

    if not grid or not grid[0]:
        return []

    rows = range(0, len(grid), 2)
    cols = range(0, len(grid[0]), 2)

    out = []
    for i in rows:
        out_row = [grid[i][j] for j in cols]
        out.append(out_row)

    return out