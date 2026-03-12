def transform(grid):
    size = 6
    h = len(grid)
    w = len(grid[0]) if grid else 0

    out = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(h):
        for j in range(w):
            v = grid[i][j]
            if v != 0:
                max_k = min(size - 1 - i, size - 1 - j)
                for k in range(max_k + 1):
                    out[i + k][j + k] = v
    return out