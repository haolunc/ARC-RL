def transform(grid):

    h = len(grid)
    if h == 0:
        return []
    w = len(grid[0])

    k = w // 2
    right_start = k + 1  
    out = []
    for r in range(h):
        row_out = []
        for i in range(k):
            left = grid[r][i]
            right_idx = right_start + i
            right = grid[r][right_idx] if right_idx < w else 0
            row_out.append(1 if (left != 0 or right != 0) else 0)
        out.append(row_out)
    return out