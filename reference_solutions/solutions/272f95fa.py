def transform(grid: list[list[int]]) -> list[list[int]]:

    n = len(grid)
    if n == 0:
        return grid
    m = len(grid[0])

    horizontal = [i for i in range(n) if all(grid[i][j] == 8 for j in range(m))]

    vertical = [j for j in range(m) if all(grid[i][j] == 8 for i in range(n))]

    res = [row[:] for row in grid]

    if len(horizontal) >= 2 and len(vertical) >= 2:
        r1, r2 = sorted(horizontal)[:2]
        c1, c2 = sorted(vertical)[:2]

        for i in range(0, r1):
            for j in range(c1 + 1, c2):
                res[i][j] = 2

        for i in range(r1 + 1, r2):

            for j in range(0, c1):
                res[i][j] = 4

            for j in range(c1 + 1, c2):
                res[i][j] = 6

            for j in range(c2 + 1, m):
                res[i][j] = 3

        for i in range(r2 + 1, n):
            for j in range(c1 + 1, c2):
                res[i][j] = 1

    return res