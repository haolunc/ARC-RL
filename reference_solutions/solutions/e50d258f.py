def transform(grid):

    R = len(grid)
    C = len(grid[0]) if R else 0

    visited = [[False] * C for _ in range(R)]

    best_twos = -1
    best_bbox = None  

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(R):
        for c in range(C):
            if grid[r][c] == 0 or visited[r][c]:
                continue

            queue = [(r, c)]
            visited[r][c] = True
            cells = []
            twos = 0

            while queue:
                x, y = queue.pop()
                cells.append((x, y))
                if grid[x][y] == 2:
                    twos += 1

                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < R and 0 <= ny < C:
                        if not visited[nx][ny] and grid[nx][ny] != 0:
                            visited[nx][ny] = True
                            queue.append((nx, ny))

            min_r = min(p[0] for p in cells)
            max_r = max(p[0] for p in cells)
            min_c = min(p[1] for p in cells)
            max_c = max(p[1] for p in cells)

            if twos > best_twos:
                best_twos = twos
                best_bbox = (min_r, max_r, min_c, max_c)

    if best_bbox is None:          
        return []

    r0, r1, c0, c1 = best_bbox
    return [grid[r][c0:c1 + 1] for r in range(r0, r1 + 1)]