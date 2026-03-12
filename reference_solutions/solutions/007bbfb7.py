def transform(grid):
    n = len(grid)
    size = n * n
    out = [[0 for _ in range(size)] for _ in range(size)]

    for br in range(n):
        for bc in range(n):
            if grid[br][bc] != 0:
                for i in range(n):
                    for j in range(n):
                        out[br * n + i][bc * n + j] = grid[i][j]
    return out