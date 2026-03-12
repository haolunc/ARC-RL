def transform(grid):
    from collections import deque

    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0])

    g = [row[:] for row in grid]

    seeds = []

    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v != 6 and v != 7:
                seeds.append((r, c, v))

    for sr, sc, color in seeds:
        dq = deque()

        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = sr + dr, sc + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if g[nr][nc] == 6:
                    g[nr][nc] = color
                    dq.append((nr, nc))

        while dq:
            cr, cc = dq.popleft()
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if g[nr][nc] == 6:
                        g[nr][nc] = color
                        dq.append((nr, nc))

    for sr, sc, _ in seeds:
        g[sr][sc] = 7

    return g