def transform(grid):
    n = len(grid)
    m = len(grid[0]) if n > 0 else 0
    out = [[0 for _ in range(m)] for _ in range(n)]

    for r in range(n):
        for c in range(m):
            if grid[r][c] == 5:
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < n and 0 <= nc < m:
                            out[nr][nc] = 1
    return out