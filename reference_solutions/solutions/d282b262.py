def transform(grid):

    h = len(grid)
    w = len(grid[0])

    visited = [[False] * w for _ in range(h)]
    comps = []                     
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 0 and not visited[r][c]:

                stack = [(r,c)]
                visited[r][c] = True
                cells = []
                while stack:
                    cr, cc = stack.pop()
                    cells.append((cr, cc, grid[cr][cc]))
                    for dr, dc in dirs:
                        nr, nc = cr+dr, cc+dc
                        if 0 <= nr < h and 0 <= nc < w                           and grid[nr][nc] != 0 and not visited[nr][nc]:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                comps.append(cells)

    def comp_key(cells):
        min_c = min(c for _, c, _ in cells)
        min_r = min(r for r, _, _ in cells)

        return (-min_c, -min_r)

    comps.sort(key=comp_key)

    out = [[0] * w for _ in range(h)]

    for cells in comps:
        max_c = max(c for _, c, _ in cells)
        max_delta = w - 1 - max_c          

        for delta in range(max_delta, -1, -1):
            ok = True
            for r, c, _ in cells:
                nc = c + delta
                if out[r][nc] != 0:        
                    ok = False
                    break
            if ok:

                for r, c, val in cells:
                    out[r][c + delta] = val
                break

    return out