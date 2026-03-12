def transform(grid):

    if not grid:
        return []

    h = len(grid)
    w = len(grid[0])

    new_grid = [[0 for _ in range(w)] for _ in range(h)]

    for i in range(1, h):
        new_grid[i] = list(grid[i - 1])   

    return new_grid