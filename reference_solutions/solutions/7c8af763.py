def transform(grid):

    h = len(grid)
    w = len(grid[0])

    result = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0 and not visited[r][c]:

                component = []
                queue = [(r, c)]
                visited[r][c] = True
                while queue:
                    x, y = queue.pop()
                    component.append((x, y))
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w:
                            if not visited[nx][ny] and grid[nx][ny] == 0:
                                visited[nx][ny] = True
                                queue.append((nx, ny))

                cnt1 = cnt2 = 0
                for x, y in component:
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w:
                            neigh = grid[nx][ny]
                            if neigh == 1:
                                cnt1 += 1
                            elif neigh == 2:
                                cnt2 += 1

                colour = 1 if cnt1 >= cnt2 else 2

                for x, y in component:
                    result[x][y] = colour

    return result