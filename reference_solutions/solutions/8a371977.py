def transform(grid):

    H = len(grid)
    W = len(grid[0])

    wall_row = [all(cell == 1 for cell in grid[i]) for i in range(H)]
    wall_col = [all(grid[i][j] == 1 for i in range(H)) for j in range(W)]

    row_block = [-1] * H
    cur = -1
    i = 0
    while i < H:
        if not wall_row[i]:
            cur += 1
            while i < H and not wall_row[i]:
                row_block[i] = cur
                i += 1
        else:
            i += 1
    max_row_block = cur

    col_block = [-1] * W
    cur = -1
    j = 0
    while j < W:
        if not wall_col[j]:
            cur += 1
            while j < W and not wall_col[j]:
                col_block[j] = cur
                j += 1
        else:
            j += 1
    max_col_block = cur

    out = [row[:] for row in grid]          
    for i in range(H):
        for j in range(W):
            if grid[i][j] == 0:
                rb = row_block[i]
                cb = col_block[j]
                if (rb == 0 or rb == max_row_block or
                    cb == 0 or cb == max_col_block):
                    out[i][j] = 2
                else:
                    out[i][j] = 3
    return out