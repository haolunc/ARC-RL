def transform(grid):

    uniform_row = None
    for i, row in enumerate(grid):
        if row[0] == row[1] == row[2]:
            uniform_row = i
            break

    out = [[0] * 9 for _ in range(9)]

    if uniform_row is not None:

        for i in range(3):
            out[uniform_row * 3 + i] = grid[i] * 3
        return out

    uniform_col = None
    for j in range(3):
        if grid[0][j] == grid[1][j] == grid[2][j]:
            uniform_col = j
            break

    if uniform_col is not None:

        for i in range(9):
            src_row = grid[i % 3]
            start = uniform_col * 3
            out[i][start:start + 3] = src_row

    return out