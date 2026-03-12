def transform(grid):
    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0])

    zero_cols = sorted({j for i in range(rows) for j in range(cols) if grid[i][j] == 0})

    color_map = {col: idx + 1 for idx, col in enumerate(zero_cols)}

    out = [row[:] for row in grid]
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 0:
                out[i][j] = color_map[j]
    return out