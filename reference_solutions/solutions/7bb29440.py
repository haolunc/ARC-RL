def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    def neighbours(r, c):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                yield nr, nc

    visited = [[False] * cols for _ in range(rows)]

    best_special = None   
    best_size = -1        
    best_bbox = None      

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 or visited[r][c]:
                continue

            stack = [(r, c)]
            visited[r][c] = True
            cells = []
            special_cnt = 0

            while stack:
                x, y = stack.pop()
                cells.append((x, y))
                if grid[x][y] != 1:        
                    special_cnt += 1
                for nx, ny in neighbours(x, y):
                    if not visited[nx][ny] and grid[nx][ny] != 0:
                        visited[nx][ny] = True
                        stack.append((nx, ny))

            r_min = min(p[0] for p in cells)
            r_max = max(p[0] for p in cells)
            c_min = min(p[1] for p in cells)
            c_max = max(p[1] for p in cells)
            size = len(cells)

            if (best_special is None or
                special_cnt < best_special or
                (special_cnt == best_special and size > best_size)):
                best_special = special_cnt
                best_size = size
                best_bbox = (r_min, r_max, c_min, c_max)

    r0, r1, c0, c1 = best_bbox
    result = [row[c0:c1 + 1] for row in grid[r0:r1 + 1]]
    return result