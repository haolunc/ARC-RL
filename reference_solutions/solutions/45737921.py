def transform(grid):

    from collections import deque

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for i in range(h):
        for j in range(w):
            if grid[i][j] == 0 or visited[i][j]:
                continue

            q = deque()
            q.append((i, j))
            visited[i][j] = True
            cells = []          
            colours = set()     

            while q:
                x, y = q.popleft()
                cells.append((x, y))
                colours.add(grid[x][y])

                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w:
                        if not visited[nx][ny] and grid[nx][ny] != 0:
                            visited[nx][ny] = True
                            q.append((nx, ny))

            if len(colours) == 2:
                c1, c2 = tuple(colours)
                for x, y in cells:
                    out[x][y] = c2 if grid[x][y] == c1 else c1

    return out