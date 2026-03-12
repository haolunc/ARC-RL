def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    out = [row[:] for row in grid]

    for r in range(rows):
        for c in range(cols):
            if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                out[r][c] = 8
    return out