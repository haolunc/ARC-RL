def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0

    col_counts = [0] * W
    for r in range(H):
        for c in range(W):
            if grid[r][c] == 2:
                col_counts[c] += 1

    cols_with_2 = [c for c, cnt in enumerate(col_counts) if cnt >= 2]
    left_col = min(cols_with_2)
    right_col = max(cols_with_2)

    left_rows = [r for r in range(H) if grid[r][left_col] == 2]
    right_rows = [r for r in range(H) if grid[r][right_col] == 2]

    for r in left_rows:

        try:
            c8 = grid[r].index(8)
        except ValueError:
            continue          

        for c in range(left_col + 1, c8):
            grid[r][c] = 8
        grid[r][c8] = 4        

    for r in right_rows:
        try:
            c8 = grid[r].index(8)
        except ValueError:
            continue
        for c in range(c8 + 1, right_col):
            grid[r][c] = 8
        grid[r][c8] = 4

    for i in range(min(len(left_rows), len(right_rows))):
        r = left_rows[i]
        s = right_rows[i]

        left_has_8 = any(v == 8 for v in grid[r])
        right_has_8 = any(v == 8 for v in grid[s])

        if left_has_8:

            for c in range(0, right_col):
                grid[s][c] = 8

        if right_has_8:

            for c in range(left_col + 1, W):
                grid[r][c] = 8

    return grid