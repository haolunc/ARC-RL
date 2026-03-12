def transform(grid):
    n = len(grid)
    if n == 0:
        return grid
    m = len(grid[0])

    result = [row[:] for row in grid]
    visited = [[False] * m for _ in range(n)]

    for r in range(n):
        for c in range(m):
            if grid[r][c] == 1 and not visited[r][c]:

                stack = [(r, c)]
                comp = []
                visited[r][c] = True
                while stack:
                    x, y = stack.pop()
                    comp.append((x, y))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < n and 0 <= ny < m and not visited[nx][ny] and grid[nx][ny] == 1:
                            visited[nx][ny] = True
                            stack.append((nx, ny))

                rs = [p[0] for p in comp]
                cs = [p[1] for p in comp]
                min_r, max_r = min(rs), max(rs)
                min_c, max_c = min(cs), max(cs)

                if (max_r - min_r) >= 1 and (max_c - min_c) >= 1:

                    border = set()
                    for cc in range(min_c, max_c + 1):
                        border.add((min_r, cc))
                        border.add((max_r, cc))
                    for rr in range(min_r, max_r + 1):
                        border.add((rr, min_c))
                        border.add((rr, max_c))

                    comp_set = set(comp)
                    if comp_set == border:

                        for (rr, cc) in comp:
                            result[rr][cc] = 3
    return result