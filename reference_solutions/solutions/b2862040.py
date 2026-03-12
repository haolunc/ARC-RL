def transform(grid):

    h = len(grid)
    w = len(grid[0])
    visited = [[False] * w for _ in range(h)]

    neigh = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for i in range(h):
        for j in range(w):
            if grid[i][j] != 1 or visited[i][j]:
                continue

            stack = [(i, j)]
            visited[i][j] = True
            cells = []          
            edge_cnt = 0        

            while stack:
                x, y = stack.pop()
                cells.append((x, y))

                for dx, dy in ((0, 1), (1, 0)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w and grid[nx][ny] == 1:
                        edge_cnt += 1

                for dx, dy in neigh:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w and grid[nx][ny] == 1 and not visited[nx][ny]:
                        visited[nx][ny] = True
                        stack.append((nx, ny))

            if edge_cnt >= len(cells):          
                for x, y in cells:
                    grid[x][y] = 8

    return grid