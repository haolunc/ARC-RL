def transform(grid):

    n = len(grid)
    m = len(grid[0]) if n else 0

    out = [row[:] for row in grid]

    ones = [(i, j) for i in range(n) for j in range(m) if grid[i][j] == 1]

    for i, j in ones:

        for col in range(m):
            out[i][col] = 1

        for row in range(n):
            out[row][j] = 1

        for di, dj in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < m:
                out[ni][nj] = 3

        out[i][j] = 2

    return out