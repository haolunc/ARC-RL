def transform(grid):

    from collections import deque

    h = len(grid)
    w = len(grid[0])

    out = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for y in range(h):
        for x in range(w):
            if grid[y][x] != 2 or visited[y][x]:
                continue

            q = deque()
            q.append((y, x))
            visited[y][x] = True
            cells = []

            min_x = max_x = x
            min_y = max_y = y

            while q:
                cy, cx = q.popleft()
                cells.append((cy, cx))
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)

                for dy, dx in dirs:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        if not visited[ny][nx] and grid[ny][nx] == 2:
                            visited[ny][nx] = True
                            q.append((ny, nx))

            width = max_x - min_x + 1
            height = max_y - min_y + 1
            size = min(width, height)

            fill_colour = {0: 3, 1: 4, 2: 8}[size % 3]

            for iy in range(min_y + 1, max_y):
                for ix in range(min_x + 1, max_x):
                    if out[iy][ix] == 0:          
                        out[iy][ix] = fill_colour

    return out