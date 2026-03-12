def transform(grid):

    from collections import deque
    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    for c in range(w):
        if grid[0][c] == 1:          
            for r in range(h):
                out[r][c] = 1

    for r in range(h):
        if grid[r][0] == 1:          
            for c in range(w):
                out[r][c] = 1

    q = deque()
    for r in range(h):
        for c in range(w):
            if out[r][c] == 1:
                q.append((r, c))

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while q:
        r, c = q.popleft()
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and out[nr][nc] == 2:
                out[nr][nc] = 1
                q.append((nr, nc))

    return out