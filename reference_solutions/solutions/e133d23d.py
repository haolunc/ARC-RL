def transform(grid):

    out = []
    for r in range(3):
        new_row = []
        for c in range(3):
            left = grid[r][c]
            right = grid[r][c + 4]   
            new_row.append(2 if (left != 0 or right != 0) else 0)
        out.append(new_row)
    return out