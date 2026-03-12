def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    N = max(val for row in grid for val in row if val != 0)

    return [[((i % N) * (j % N)) % N + 1 for j in range(w)] for i in range(h)]