def transform(grid):

    n = len(grid)
    if n == 0:
        return grid
    m = len(grid[0])
    out = [row[:] for row in grid]

    for c in range(-n + 1, m):
        positions = []
        i_start = max(0, -c)
        i_end = min(n - 1, m - 1 - c)
        for i in range(i_start, i_end + 1):
            j = i + c
            if grid[i][j] != 0:
                positions.append((i, j))

        for t, (i, j) in enumerate(positions):
            if t % 2 == 1:
                out[i][j] = 4
    return out