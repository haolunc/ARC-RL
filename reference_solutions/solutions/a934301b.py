def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0
    result = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0 or visited[r][c]:
                continue

            stack = [(r, c)]
            visited[r][c] = True
            cells = [(r, c)]
            eight_cnt = 1 if grid[r][c] == 8 else 0

            while stack:
                x, y = stack.pop()
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w:
                        if not visited[nx][ny] and grid[nx][ny] != 0:
                            visited[nx][ny] = True
                            stack.append((nx, ny))
                            cells.append((nx, ny))
                            if grid[nx][ny] == 8:
                                eight_cnt += 1

            if eight_cnt > 1:
                for x, y in cells:
                    result[x][y] = 0

    return result