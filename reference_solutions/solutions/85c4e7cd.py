def transform(grid):
    n = len(grid)

    L = (n + 1) // 2

    layer_colors = [grid[d][d] for d in range(L)]

    res = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            d = min(i, j, n - 1 - i, n - 1 - j)
            res[i][j] = layer_colors[L - 1 - d]
    return res