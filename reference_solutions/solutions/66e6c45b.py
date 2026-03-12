def transform(grid: list[list[int]]) -> list[list[int]]:
    n = len(grid)
    m = len(grid[0]) if n > 0 else 0

    out = [[0 for _ in range(n)] for _ in range(n)]
    if n >= 3 and m >= 3:
        out[0][0] = grid[1][1]
        out[0][n - 1] = grid[1][2] if m > 2 else 0
        out[n - 1][0] = grid[2][1] if n > 2 else 0
        out[n - 1][n - 1] = grid[2][2] if (n > 2 and m > 2) else 0
    return out