def transform(grid):

    h = len(grid)
    w = len(grid[0])

    rows_with_1 = [r for r in range(h) if 1 in grid[r]]
    cols_with_1 = [c for c in range(w) if any(grid[r][c] == 1 for r in range(h))]

    min_r, max_r = min(rows_with_1), max(rows_with_1)
    min_c, max_c = min(cols_with_1), max(cols_with_1)

    interior_rows = range(min_r + 1, max_r)
    interior_cols = range(min_c + 1, max_c)

    freq = {}
    for r in interior_rows:
        for c in interior_cols:
            col = grid[r][c]
            if col != 0 and col != 1:
                freq[col] = freq.get(col, 0) + 1

    if not freq:
        target = 0
        count = 0
    else:
        target = max(freq, key=lambda k: freq[k])
        count = freq[target]

    out = [[0, 0, 0] for _ in range(3)]

    order = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0)]

    for i in range(min(count, 6)):
        r, c = order[i]
        out[r][c] = target

    return out