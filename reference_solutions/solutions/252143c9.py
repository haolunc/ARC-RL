def transform(grid):

    n = len(grid)
    if n == 0:
        return grid
    m = len(grid[0])

    N = min(n, m)

    c = grid[N // 2][N // 2]

    out = [[7 for _ in range(n)] for _ in range(n)]

    for i in range(N):
        j = N - 1 - i
        if c == 0:
            if i <= N // 2:
                out[i][j] = 0
            else:
                out[i][j] = 7  
        else:
            if i < N // 2:
                out[i][j] = 7
            else:
                out[i][j] = c

    return out