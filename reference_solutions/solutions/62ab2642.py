def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    visited = [[False] * w for _ in range(h)]

    components = []

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0 and not visited[r][c]:

                comp = []
                stack = [(r, c)]
                visited[r][c] = True
                while stack:
                    x, y = stack.pop()
                    comp.append((x, y))
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w:
                            if grid[nx][ny] == 0 and not visited[nx][ny]:
                                visited[nx][ny] = True
                                stack.append((nx, ny))
                components.append(comp)

    if not components:
        return [row[:] for row in grid]

    smallest = min(components, key=len)
    largest = max(components, key=len)

    out = [row[:] for row in grid]          
    for r, c in smallest:
        out[r][c] = 7
    for r, c in largest:
        out[r][c] = 8

    return out