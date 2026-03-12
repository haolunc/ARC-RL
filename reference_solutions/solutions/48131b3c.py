def transform(grid):

    n = len(grid)
    if n == 0:
        return []

    M = max(max(row) for row in grid)

    C = [[M - grid[i][j] for j in range(n)] for i in range(n)]

    res = [[C[i % n][j % n] for j in range(2 * n)] for i in range(2 * n)]
    return res