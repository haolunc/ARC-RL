def transform(grid: list[list[int]]) -> list[list[int]]:

    n = len(grid)
    g = [row[:] for row in grid]

    centers = []

    for r in range(n - 4):
        for c in range(n - 4):

            top = all(g[r][c + k] == 1 for k in range(5))

            bot = all(g[r + 4][c + k] == 1 for k in range(5))

            left = all(g[r + i][c] == 1 for i in range(1, 4))

            right = all(g[r + i][c + 4] == 1 for i in range(1, 4))

            interior_not_all_one = not all(
                g[r + i][c + j] == 1 for i in range(1, 4) for j in range(1, 4)
            )
            if top and bot and left and right and interior_not_all_one:
                centers.append((r + 2, c + 2))

    for rr, cc in centers:

        for j in range(n):
            if g[rr][j] != 1:
                g[rr][j] = 6

        for i in range(n):
            if g[i][cc] != 1:
                g[i][cc] = 6

    return g