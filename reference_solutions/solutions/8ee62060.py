def transform(grid: list[list[int]]) -> list[list[int]]:

    h = len(grid)
    w = len(grid[0])

    new_grid = [[0] * w for _ in range(h)]

    for c in range(0, w, 2):

        new_c = w - 2 - c
        for r in range(h):

            new_grid[r][new_c] = grid[r][c]
            new_grid[r][new_c + 1] = grid[r][c + 1]

    return new_grid