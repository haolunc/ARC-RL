def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    out = [[0 for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                for rr in range(rows):
                    out[rr][c] = 2

    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            if val != 0 and val != 2:
                for cc in range(cols):
                    out[r][cc] = val

    return out