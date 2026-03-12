def transform(grid):
    from collections import deque, Counter

    h, w = len(grid), len(grid[0])

    flat = [c for row in grid for c in row]
    bg = Counter(flat).most_common(1)[0][0]

    visited = [[False] * w for _ in range(h)]
    comps_by_colour = {}          

    for r in range(h):
        for c in range(w):
            if visited[r][c]:
                continue
            colour = grid[r][c]
            visited[r][c] = True

            if colour == bg:
                continue
            q = deque([(r, c)])
            cells = [(r, c)]
            while q:
                cr, cc = q.popleft()
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = cr+dr, cc+dc
                    if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and grid[nr][nc]==colour:
                        visited[nr][nc] = True
                        q.append((nr,nc))
                        cells.append((nr,nc))
            comps_by_colour.setdefault(colour, []).append(cells)

    out = [[bg]*w for _ in range(h)]

    for colour, comps in comps_by_colour.items():
        if len(comps) <= 1:          
            for comp in comps:
                for r,c in comp:
                    out[r][c] = colour
            continue

        for comp in comps:

            min_r = min(r for r,_ in comp)
            max_r = max(r for r,_ in comp)
            min_c = min(c for _,c in comp)
            max_c = max(c for _,c in comp)
            height = max_r - min_r + 1
            width  = max_c - min_c + 1

            dr = height if min_r == 0 else (-height if max_r == h-1 else 0)
            dc = width  if min_c == 0 else (-width if max_c == w-1 else 0)

            for r,c in comp:
                nr, nc = r + dr, c + dc
                out[nr][nc] = colour

    return out