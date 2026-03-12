def transform(grid):
    n = len(grid)

    h = [list(reversed(row)) for row in grid]

    v = list(reversed(grid))

    r = [list(reversed(row)) for row in reversed(grid)]

    top = [grid[i] + h[i] for i in range(n)]
    bottom = [v[i] + r[i] for i in range(n)]
    return top + bottom