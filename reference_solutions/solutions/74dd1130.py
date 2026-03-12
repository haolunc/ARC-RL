def transform(grid):
    if not grid:
        return []
    rows = len(grid)
    cols = len(grid[0])
    return [[grid[r][c] for r in range(rows)] for c in range(cols)]