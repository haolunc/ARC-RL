def transform(grid):
    n = len(grid)
    mid = n // 2
    bottom = grid[mid:]
    top = bottom[::-1]
    return top + bottom