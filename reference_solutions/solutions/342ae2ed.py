def transform(grid):
    import collections

    h = len(grid)
    w = len(grid[0])
    bg = 7  

    def get_components(col):
        visited = [[False]*w for _ in range(h)]
        comps = []
        for i in range(h):
            for j in range(w):
                if not visited[i][j] and grid[i][j] == col:
                    q = collections.deque([(i,j)])
                    visited[i][j] = True
                    comp = []
                    while q:
                        r,c = q.popleft()
                        comp.append((r,c))
                        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                            nr,nc = r+dr, c+dc
                            if 0<=nr<h and 0<=nc<w and not visited[nr][nc] and grid[nr][nc]==col:
                                visited[nr][nc] = True
                                q.append((nr,nc))
                    comps.append(comp)
        return comps

    out = [row[:] for row in grid]

    colours = {grid[i][j] for i in range(h) for j in range(w) if grid[i][j] != bg}
    for col in colours:
        comps = get_components(col)
        if len(comps) != 2:
            continue          
        comp_a, comp_b = comps

        best = None
        best_dist = None
        for a in comp_a:
            for b in comp_b:
                dr = b[0] - a[0]
                dc = b[1] - a[1]
                if abs(dr) == abs(dc) and dr != 0:   
                    dist = abs(dr)
                    if best_dist is None or dist < best_dist:
                        best_dist = dist
                        best = (a, b)

        if best is None:
            continue  

        (ar, ac), (br, bc) = best
        step_r = 1 if br > ar else -1
        step_c = 1 if bc > ac else -1

        r, c = ar + step_r, ac + step_c
        while (r, c) != (br, bc):
            if out[r][c] == bg:        
                out[r][c] = col
            r += step_r
            c += step_c

    return out