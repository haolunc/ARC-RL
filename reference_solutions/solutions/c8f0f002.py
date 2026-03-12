def transform(grid):
    return [[5 if val == 7 else val for val in row] for row in grid]