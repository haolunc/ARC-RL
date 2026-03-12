def transform(grid):
    from collections import deque, Counter
    if not grid:
        return grid
    n = len(grid)
    m = len(grid[0])

    res = [row[:] for row in grid]
    visited = [[False] * m for _ in range(n)]

    for i in range(n):
        for j in range(m):
            if grid[i][j] == 5 and not visited[i][j]:

                q = deque()
                q.append((i, j))
                visited[i][j] = True
                comp = []
                cols = set()

                while q:
                    x, y = q.popleft()
                    comp.append((x, y))
                    cols.add(y)
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < n and 0 <= ny < m and not visited[nx][ny] and grid[nx][ny] == 5:
                            visited[nx][ny] = True
                            q.append((nx, ny))

                top_colors = Counter()
                for c in cols:
                    if 0 <= c < m:
                        val = grid[0][c]
                        if val != 0:
                            top_colors[val] += 1
                if top_colors:
                    color_to_fill = top_colors.most_common(1)[0][0]
                else:
                    color_to_fill = 0  

                for x, y in comp:
                    res[x][y] = color_to_fill
    return res