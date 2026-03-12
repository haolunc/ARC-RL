def transform(grid):

    r8 = c8 = r2 = c2 = None
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == 8:
                r8, c8 = r, c
            elif val == 2:
                r2, c2 = r, c

    for r in range(min(r8, r2), max(r8, r2) + 1):
        if grid[r][c8] not in (8, 2):
            grid[r][c8] = 4

    for c in range(min(c8, c2), max(c8, c2) + 1):
        if grid[r2][c] not in (8, 2):
            grid[r2][c] = 4
    return grid