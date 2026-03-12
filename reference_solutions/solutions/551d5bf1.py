def transform(grid):

    H = len(grid)
    W = len(grid[0])

    out = [row[:] for row in grid]

    visited = [[False] * W for _ in range(H)]

    from collections import deque

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(H):
        for c in range(W):
            if grid[r][c] != 1 or visited[r][c]:
                continue

            q = deque()
            q.append((r, c))
            min_r = max_r = r
            min_c = max_c = c

            while q:
                x, y = q.popleft()
                if visited[x][y]:
                    continue
                visited[x][y] = True

                if x < min_r:
                    min_r = x
                if x > max_r:
                    max_r = x
                if y < min_c:
                    min_c = y
                if y > max_c:
                    max_c = y

                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < H and 0 <= ny < W and not visited[nx][ny] and grid[nx][ny] == 1:
                        q.append((nx, ny))

            for i in range(min_r, max_r + 1):
                for j in range(min_c, max_c + 1):
                    if out[i][j] == 0:          
                        out[i][j] = 8

            for j in range(min_c, max_c + 1):
                if grid[min_r][j] == 0:          
                    for i in range(min_r - 1, -1, -1):
                        if grid[i][j] == 1:
                            break
                        out[i][j] = 8

            for j in range(min_c, max_c + 1):
                if grid[max_r][j] == 0:
                    for i in range(max_r + 1, H):
                        if grid[i][j] == 1:
                            break
                        out[i][j] = 8

            for i in range(min_r, max_r + 1):
                if grid[i][min_c] == 0:
                    for j in range(min_c - 1, -1, -1):
                        if grid[i][j] == 1:
                            break
                        out[i][j] = 8

            for i in range(min_r, max_r + 1):
                if grid[i][max_c] == 0:
                    for j in range(max_c + 1, W):
                        if grid[i][j] == 1:
                            break
                        out[i][j] = 8

    return out