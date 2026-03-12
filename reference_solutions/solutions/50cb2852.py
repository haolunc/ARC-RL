def transform(grid):

    H = len(grid)
    if H == 0:
        return []
    W = len(grid[0])

    out = [row[:] for row in grid]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(H):
        for c in range(W):
            v = grid[r][c]
            if v == 0:
                continue

            interior = True
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc

                if not (0 <= nr < H and 0 <= nc < W):
                    interior = False
                    break

                if grid[nr][nc] != v:
                    interior = False
                    break

            if interior:
                out[r][c] = 8

    return out