def transform(grid):

    import copy
    rows = len(grid)
    cols = len(grid[0])
    result = copy.deepcopy(grid)

    visited = [[False] * cols for _ in range(rows)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 3 or visited[r][c]:
                continue

            stack = [(r, c)]
            component = []
            visited[r][c] = True
            while stack:
                cr, cc = stack.pop()
                component.append((cr, cc))
                for dr, dc in dirs:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols                            and not visited[nr][nc] and grid[nr][nc] == 3:
                        visited[nr][nc] = True
                        stack.append((nr, nc))

            min_r = min(p[0] for p in component)
            max_r = max(p[0] for p in component)
            min_c = min(p[1] for p in component)
            max_c = max(p[1] for p in component)
            comp_h = max_r - min_r + 1
            comp_w = max_c - min_c + 1

            k = 1
            while True:
                added = False
                for sign in (-1, 1):          
                    dr = k * comp_h
                    dc = sign * k * comp_w
                    for (pr, pc) in component:
                        nr = pr + dr
                        nc = pc + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if result[nr][nc] != 3:
                                result[nr][nc] = 3
                                added = True
                if not added:
                    break
                k += 1

    return result