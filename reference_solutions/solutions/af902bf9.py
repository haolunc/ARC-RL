def transform(grid):

    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    out = [row[:] for row in grid]

    for r1 in range(rows - 1):
        for r2 in range(r1 + 1, rows):

            common_cols = [c for c in range(cols) if grid[r1][c] == 4 and grid[r2][c] == 4]
            if len(common_cols) >= 2:
                m = len(common_cols)
                for i in range(m):
                    for j in range(i + 1, m):
                        c1 = common_cols[i]
                        c2 = common_cols[j]

                        for r in range(r1 + 1, r2):
                            for c in range(c1 + 1, c2):
                                out[r][c] = 2
    return out