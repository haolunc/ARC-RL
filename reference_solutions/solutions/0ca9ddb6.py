def transform(grid):

    n = len(grid)
    m = len(grid[0]) if n else 0

    out = [row[:] for row in grid]

    orthogonal = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    diagonal   = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for r in range(n):
        for c in range(m):
            val = grid[r][c]
            if val == 1:
                for dr, dc in orthogonal:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < m and out[nr][nc] == 0:
                        out[nr][nc] = 7
            elif val == 2:
                for dr, dc in diagonal:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < m and out[nr][nc] == 0:
                        out[nr][nc] = 4
    return out