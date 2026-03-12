def transform(grid):

    import collections
    h = len(grid)
    w = len(grid[0]) if h else 0

    pat_rows = [i for i in range(h) for j in range(w) if grid[i][j] not in (0, 5)]
    pat_cols = [j for j in range(w) for i in range(h) if grid[i][j] not in (0, 5)]

    if not pat_rows:

        return [row[:] for row in grid]

    rmin, rmax = min(pat_rows), max(pat_rows)
    cmin, cmax = min(pat_cols), max(pat_cols)

    pattern = [row[cmin:cmax + 1] for row in grid[rmin:rmax + 1]]

    visited = [[False] * w for _ in range(h)]
    to_fill = []          

    for i in range(h):
        for j in range(w):
            if grid[i][j] == 5 and not visited[i][j]:

                q = collections.deque()
                q.append((i, j))
                visited[i][j] = True
                cells = [(i, j)]
                while q:
                    y, x = q.popleft()
                    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w and not visited[ny][nx] and grid[ny][nx] == 5:
                            visited[ny][nx] = True
                            q.append((ny, nx))
                            cells.append((ny, nx))

                rows = [r for r, _ in cells]
                cols = [c for _, c in cells]
                r0, r1 = min(rows), max(rows)
                c0, c1 = min(cols), max(cols)

                to_fill.append((r0, c0, r1 - r0 + 1, c1 - c0 + 1))

    new_grid = [row[:] for row in grid]  

    pat_h = len(pattern)
    pat_w = len(pattern[0])

    for r0, c0, h5, w5 in to_fill:

        h_copy = min(pat_h, h5)
        w_copy = min(pat_w, w5)
        for dr in range(h_copy):
            for dc in range(w_copy):
                new_grid[r0 + dr][c0 + dc] = pattern[dr][dc]

    return new_grid