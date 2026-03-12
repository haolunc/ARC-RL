def transform(grid):

    h = len(grid)
    if h == 0:
        return grid
    w = len(grid[0])

    out = [[7 for _ in range(w)] for _ in range(h)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 8:
                out[r][c] = 8

    visited = [[False] * w for _ in range(h)]

    dirs = [(-1,0),(1,0),(0,-1),(0,1)]

    for r in range(h):
        for c in range(w):
            val = grid[r][c]

            if val != 7 and val != 8 and not visited[r][c]:

                stack = [(r, c)]
                comp = []
                visited[r][c] = True
                while stack:
                    x, y = stack.pop()
                    comp.append((x, y))
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w:
                            if not visited[nx][ny] and grid[nx][ny] == val:
                                visited[nx][ny] = True
                                stack.append((nx, ny))

                s = len(comp)
                for (x, y) in comp:
                    nx = x - s

                    if 0 <= nx < h:
                        out[nx][y] = val

    return out