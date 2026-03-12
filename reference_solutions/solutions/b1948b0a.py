def transform(grid):
    return [[2 if v == 6 else v for v in row] for row in grid]