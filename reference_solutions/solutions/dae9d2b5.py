def transform(grid):

    rows = len(grid)
    cols = len(grid[0])
    half = cols // 2          

    out = []
    for r in range(rows):
        out_row = []
        for c in range(half):
            left = grid[r][c]
            right = grid[r][c + half]
            out_row.append(6 if (left == 4 or right == 3) else 0)
        out.append(out_row)

    return out