def transform(grid):

    if not grid:
        return grid

    h, w = len(grid), len(grid[0])
    visited = [[False] * w for _ in range(h)]
    components = []          

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(h):
        for c in range(w):
            if not visited[r][c] and grid[r][c] == 4:
                stack = [(r, c)]
                visited[r][c] = True
                cells = set()
                while stack:
                    x, y = stack.pop()
                    cells.add((x, y))
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w:
                            if not visited[nx][ny] and grid[nx][ny] == 4:
                                visited[nx][ny] = True
                                stack.append((nx, ny))
                components.append( (cells, len(cells)) )
                components.append((cells, len(cells)))  

    if not components:
        return [row[:] for row in grid]

    max_size = max(sz for _, sz in components)

    out = [row[:] for row in grid]

    for cells, size in components:
        fill_colour = 2 if size == max_size else 1
        for x, y in cells:

            if ((x - 1, y) in cells and (x + 1, y) in cells and
                (x, y - 1) in cells and (x, y + 1) in cells):
                out[x][y] = fill_colour

    return out