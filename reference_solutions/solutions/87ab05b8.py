def transform(grid):

    pos = None
    for i, row in enumerate(grid):
        for j, val in enumerate(row):
            if val == 2:
                pos = (i, j)
                break
        if pos:
            break

    if pos is None:
        return [[6 for _ in row] for row in grid]

    start_row = (pos[0] // 2) * 2
    start_col = (pos[1] // 2) * 2

    out = [[6 for _ in row] for row in grid]

    rows = len(grid)
    cols = len(grid[0])
    for i in range(start_row, min(start_row + 2, rows)):
        for j in range(start_col, min(start_col + 2, cols)):
            out[i][j] = 2

    return out