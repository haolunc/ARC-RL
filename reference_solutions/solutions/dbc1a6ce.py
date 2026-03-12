def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    for r in range(h):
        cols = [c for c in range(w) if grid[r][c] == 1]
        if len(cols) >= 2:
            left, right = min(cols), max(cols)
            for c in range(left, right + 1):
                if out[r][c] == 0:      
                    out[r][c] = 8

    for c in range(w):
        rows = [r for r in range(h) if grid[r][c] == 1]
        if len(rows) >= 2:
            top, bottom = min(rows), max(rows)
            for r in range(top, bottom + 1):
                if out[r][c] == 0:
                    out[r][c] = 8

    return out