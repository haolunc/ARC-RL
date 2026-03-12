def transform(grid):

    h = len(grid)
    w = len(grid[0])
    out_rows = []

    for r in range(h - 1):

        block_cols = []
        for c in range(w - 1):
            v = grid[r][c]
            if v != 0 and v == grid[r][c + 1] == grid[r + 1][c] == grid[r + 1][c + 1]:
                block_cols.append(c)

        if len(block_cols) >= 2:
            left = block_cols[0]
            right = block_cols[-1]

            start = left + 2
            end = right  

            top_slice = grid[r][start:end]
            bot_slice = grid[r + 1][start:end]
            out_rows.append(top_slice)
            out_rows.append(bot_slice)

    return out_rows