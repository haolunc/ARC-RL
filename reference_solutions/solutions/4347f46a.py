def transform(grid):

    from collections import deque

    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    visited = [[False] * w for _ in range(h)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0 or visited[r][c]:
                continue

            colour = grid[r][c]

            q = deque()
            q.append((r, c))
            visited[r][c] = True
            component = []

            while q:
                x, y = q.popleft()
                component.append((x, y))
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w                       and not visited[nx][ny] and grid[nx][ny] == colour:
                        visited[nx][ny] = True
                        q.append((nx, ny))

            rows = [p[0] for p in component]
            cols = [p[1] for p in component]
            min_r, max_r = min(rows), max(rows)
            min_c, max_c = min(cols), max(cols)

            height = max_r - min_r + 1
            width = max_c - min_c + 1

            if len(component) == height * width:
                for x, y in component:
                    if (x != min_r and x != max_r) and (y != min_c and y != max_c):
                        grid[x][y] = 0

    return grid