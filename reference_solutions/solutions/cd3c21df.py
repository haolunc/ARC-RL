def transform(grid):

    if not grid:
        return []

    h = len(grid)
    w = len(grid[0])

    visited = [[False] * w for _ in range(h)]
    comps = {}                     

    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val == 0 or visited[r][c]:
                continue

            stack = [(r, c)]
            visited[r][c] = True
            component = []

            while stack:
                cr, cc = stack.pop()
                component.append((cr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w:
                        if not visited[nr][nc] and grid[nr][nc] == val:
                            visited[nr][nc] = True
                            stack.append((nr, nc))

            comps.setdefault(val, []).append(component)

    single_colours = [col for col, lst in comps.items() if len(lst) == 1]
    if not single_colours:                     
        return []

    chosen = min(single_colours)               
    component = comps[chosen][0]

    min_r = min(r for r, _ in component)
    max_r = max(r for r, _ in component)
    min_c = min(c for _, c in component)
    max_c = max(c for _, c in component)

    result = [grid[row][min_c:max_c + 1] for row in range(min_r, max_r + 1)]
    return result