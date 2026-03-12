def transform(grid):
    n = len(grid)
    m = len(grid[0]) if n > 0 else 0
    out = [[0 for _ in range(m)] for _ in range(n)]
    for r in range(n):
        for c in range(m):
            if grid[r][c] == 8:
                if r + 1 < n:
                    out[r + 1][c] = 2
    return out