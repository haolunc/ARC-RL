def transform(grid):

    rows = len(grid)
    cols = len(grid[0])
    half = rows // 2

    out = []
    for i in range(half):
        out_row = []
        for j in range(cols):
            a = grid[i][j]
            b = grid[i + half][j]

            out_row.append(6 if (a != 0) != (b != 0) else 0)
        out.append(out_row)

    return out