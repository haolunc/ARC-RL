def transform(grid):

    h = len(grid)
    w = len(grid[0])

    row_counts = [sum(1 for v in grid[r] if v == 3) for r in range(h)]
    centre_row = max(range(h), key=row_counts.__getitem__)

    col_counts = [sum(1 for r in range(h) if grid[r][c] == 3) for c in range(w)]
    centre_col = max(range(w), key=col_counts.__getitem__)

    out = [row[:] for row in grid]          

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0:
                if max(abs(r - centre_row), abs(c - centre_col)) % 2 == 0:
                    out[r][c] = 4
    return out