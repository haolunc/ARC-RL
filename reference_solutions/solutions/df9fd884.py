def transform(grid):

    from collections import Counter, deque

    h = len(grid)
    w = len(grid[0])

    flat = [c for row in grid for c in row]
    bg = Counter(flat).most_common(1)[0][0]

    def bfs(sr, sc, colour, visited):
        q = deque([(sr, sc)])
        comp = [(sr, sc)]
        visited.add((sr, sc))
        while q:
            r, c = q.popleft()
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if 0 <= nr < h and 0 <= nc < w and (nr,nc) not in visited:
                    if grid[nr][nc] == colour:
                        visited.add((nr,nc))
                        q.append((nr,nc))
                        comp.append((nr,nc))
        return comp

    interior_colour = None
    interior_cells = None
    visited_global = set()
    for r in range(h):
        for c in range(w):
            col = grid[r][c]
            if col == bg or (r,c) in visited_global:
                continue
            comp = bfs(r, c, col, visited_global)

            touches_lr = any(cc == 0 or cc == w-1 for (_, cc) in comp)
            if not touches_lr:
                interior_colour = col
                interior_cells = comp
                break
        if interior_colour is not None:
            break

    if interior_colour is None:

        return grid

    min_r = min(r for r, _ in interior_cells)
    min_c = min(c for _, c in interior_cells)
    shape = [(r - min_r, c - min_c) for (r, c) in interior_cells]
    shape_h = max(dr for dr, _ in shape) + 1
    shape_w = max(dc for _, dc in shape) + 1

    for r, c in interior_cells:
        grid[r][c] = bg

    candidates = []
    for r0 in range(0, h - shape_h + 1):
        for c0 in range(1, w - shape_w):          
            fits = True
            for dr, dc in shape:
                if grid[r0 + dr][c0 + dc] != bg:
                    fits = False
                    break
            if fits:
                candidates.append((r0, c0))

    max_row = max(r for r, _ in candidates)
    best = None
    best_dist = -1
    for r0, c0 in candidates:
        if r0 != max_row:
            continue
        dist = abs(c0 - min_c)
        if dist > best_dist or (dist == best_dist and (best is None or c0 > best[1])):
            best = (r0, c0)
            best_dist = dist

    new_r0, new_c0 = best

    for dr, dc in shape:
        grid[new_r0 + dr][new_c0 + dc] = interior_colour

    return grid