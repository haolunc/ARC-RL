def transform(grid):
    if not grid:
        return grid
    nrows = len(grid)
    ncols = len(grid[0])
    mid = ncols // 2
    result = [[0] * ncols for _ in range(nrows)]
    for r in range(nrows):
        result[r][mid] = grid[r][mid]
    return result