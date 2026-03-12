def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    blue_cnt = sum(1 for row in grid for val in row if val == 1)

    out = [[0 for _ in range(w)] for _ in range(h)]

    for c in range(min(blue_cnt, w)):
        out[0][c] = 2

    if blue_cnt > w and h > 1 and w > 1:
        out[1][1] = 2

    return out