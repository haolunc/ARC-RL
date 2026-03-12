def transform(grid):

    from collections import deque

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    size_to_colour = {1: 3, 2: 2, 3: 1}

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for y in range(h):
        for x in range(w):
            if grid[y][x] != 0 or visited[y][x]:
                continue          

            q = deque()
            q.append((y, x))
            visited[y][x] = True
            component = [(y, x)]

            while q:
                cy, cx = q.popleft()
                for dy, dx in dirs:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w:
                        if not visited[ny][nx] and grid[ny][nx] == 0:
                            visited[ny][nx] = True
                            q.append((ny, nx))
                            component.append((ny, nx))

            colour = size_to_colour.get(len(component), 0)   

            for cy, cx in component:
                out[cy][cx] = colour

    return out