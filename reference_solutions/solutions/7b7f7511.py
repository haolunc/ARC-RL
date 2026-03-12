def transform(grid):
    if not grid:
        return []
    rows = len(grid)
    cols = len(grid[0])
    if cols >= rows:
        new_cols = cols // 2
        return [row[:new_cols] for row in grid]
    else:
        new_rows = rows // 2
        return grid[:new_rows]