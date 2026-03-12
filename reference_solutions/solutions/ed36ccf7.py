def transform(grid):
    n = len(grid)
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            result[i][j] = grid[j][n - 1 - i]
    return result