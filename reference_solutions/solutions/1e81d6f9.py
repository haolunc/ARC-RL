def transform(grid):

    if not grid or not grid[0]:
        return grid

    target = grid[1][1]  
    rows = len(grid)
    cols = len(grid[0])

    out = [row[:] for row in grid]

    for r in range(rows):
        for c in range(cols):
            if (r, c) != (1, 1) and grid[r][c] == target:
                out[r][c] = 0
    return out