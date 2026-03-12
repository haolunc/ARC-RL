def transform(grid):

    from collections import deque
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    out = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 1 or visited[r][c]:
                continue

            q = deque()
            q.append((r, c))
            visited[r][c] = True
            component = [(r, c)]

            while q:
                cr, cc = q.popleft()
                for dr, dc in dirs:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w                       and not visited[nr][nc] and grid[nr][nc] == 1:
                        visited[nr][nc] = True
                        q.append((nr, nc))
                        component.append((nr, nc))

            minR = min(p[0] for p in component)
            maxR = max(p[0] for p in component)
            minC = min(p[1] for p in component)
            maxC = max(p[1] for p in component)

            inner_colour = None
            for i in range(minR, maxR + 1):
                for j in range(minC, maxC + 1):
                    v = grid[i][j]
                    if v != 0 and v != 1:
                        inner_colour = v
                        break
                if inner_colour is not None:
                    break

            if inner_colour is None:

                continue

            for i in range(minR - 1, maxR + 1):
                if i < 0:
                    continue
                for j in range(minC, maxC + 1):
                    if out[i][j] == 1:
                        continue
                    out[i][j] = inner_colour

    return out