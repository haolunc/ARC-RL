def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    from collections import Counter
    cnt = Counter()
    for row in grid:
        for v in row:
            if v != 0:
                cnt[v] += 1

    if not cnt:
        return [row[:] for row in grid]          
    A = max(cnt.items(), key=lambda kv: kv[1])[0]

    out = [row[:] for row in grid]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val == 0 or val == A:
                continue          

            neigh_A = 0
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == A:
                    neigh_A += 1
            out[r][c] = A if neigh_A >= 2 else 0

    return out