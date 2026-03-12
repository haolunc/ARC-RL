def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    first6 = {}
    for c in range(w):
        for r in range(h):
            if grid[r][c] == 6:
                first6[c] = r
                break

    max_row = max(first6.values())
    cols_max = [c for c, r in first6.items() if r == max_row]
    col_9 = min(cols_max)          

    min_row = min(first6.values())
    cols_min = [c for c, r in first6.items() if r == min_row]
    col_4 = max(cols_min)          

    for r in range(1, max_row):
        out[r][col_9] = 9
    for r in range(1, min_row):
        out[r][col_4] = 4

    return out