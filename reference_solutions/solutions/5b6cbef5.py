def transform(grid):

    n = len(grid)

    out = [[0 for _ in range(n * n)] for _ in range(n * n)]

    for i in range(n):
        for j in range(n):
            if grid[i][j] != 0:          
                for di in range(n):
                    for dj in range(n):
                        out[i * n + di][j * n + dj] = grid[di][dj]
    return out