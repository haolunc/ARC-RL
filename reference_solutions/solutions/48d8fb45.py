def transform(grid):

    r = c = None
    for i, row in enumerate(grid):
        for j, val in enumerate(row):
            if val == 5:
                r, c = i, j
                break
        if r is not None:
            break

    start_row = r + 1
    start_col = c - 1
    result = []
    for i in range(start_row, start_row + 3):
        result.append(grid[i][start_col:start_col + 3])
    return result