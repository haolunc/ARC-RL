def transform(grid):
    from collections import deque, defaultdict

    H = len(grid)
    W = len(grid[0]) if H>0 else 0

    g = [list(row) for row in grid]

    neigh8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    visited = [[False]*W for _ in range(H)]
    comps = []  
    for r in range(H):
        for c in range(W):
            if not visited[r][c] and g[r][c] != 0:

                q = deque()
                q.append((r,c))
                visited[r][c] = True
                comp = [(r,c)]
                while q:
                    y,x = q.popleft()
                    for dy,dx in neigh8:
                        ny, nx = y+dy, x+dx
                        if 0 <= ny < H and 0 <= nx < W and not visited[ny][nx] and g[ny][nx] != 0:
                            visited[ny][nx] = True
                            q.append((ny,nx))
                            comp.append((ny,nx))
                comps.append(comp)

    comp_sets = [set(comp) for comp in comps]

    out = [row[:] for row in g]

    for comp_idx, comp in enumerate(comps):
        comp_set = comp_sets[comp_idx]

        seeds = [(r,c,g[r][c]) for (r,c) in comp if g[r][c] != 1 and g[r][c] != 0]
        if not seeds:
            continue

        def in_comp(y,x):
            return (y,x) in comp_set

        max_window = min(max(H,W), 9)  
        windows = [3,5,7,9]
        windows = [w for w in windows if w <= max_window]

        patterns = {}
        for w in windows:
            half = w//2
            for (y,x) in comp:
                pat = []
                for dy in range(-half, half+1):
                    for dx in range(-half, half+1):
                        yy, xx = y+dy, x+dx
                        pat.append(1 if (0 <= yy < H and 0 <= xx < W and in_comp(yy,xx)) else 0)
                patterns[(y,x,w)] = tuple(pat)

        for (sy,sx,sc) in seeds:
            chosen_w = None
            chosen_pat = None
            for w in windows:
                pat = patterns.get((sy,sx,w))
                if pat is None:
                    continue

                matches = []
                for (y,x) in comp:
                    if (y,x) == (sy,sx):
                        continue
                    if patterns.get((y,x,w)) == pat:
                        matches.append((y,x))
                if matches:
                    chosen_w = w
                    chosen_pat = pat
                    break

            if chosen_w is None:
                continue

            for (y,x) in comp:
                if g[y][x] == 1 and patterns.get((y,x,chosen_w)) == chosen_pat:
                    out[y][x] = sc

    return out