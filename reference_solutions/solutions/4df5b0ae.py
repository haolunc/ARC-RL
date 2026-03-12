def transform(grid):

    H, W = len(grid), len(grid[0])

    from collections import Counter, deque
    flat = [c for row in grid for c in row]
    dominant, _ = Counter(flat).most_common(1)[0]

    visited = [[False] * W for _ in range(H)]
    comps = []                       

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(H):
        for c in range(W):
            if visited[r][c] or grid[r][c] == dominant:
                continue
            colour = grid[r][c]

            q = deque()
            q.append((r, c))
            visited[r][c] = True
            cells = []
            min_r, min_c = r, c
            max_r, max_c = r, c
            while q:
                cr, cc = q.popleft()
                cells.append((cr, cc))
                min_r = min(min_r, cr)
                min_c = min(min_c, cc)
                max_r = max(max_r, cr)
                max_c = max(max_c, cc)
                for dr, dc in dirs:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < H and 0 <= nc < W                       and not visited[nr][nc]                       and grid[nr][nc] == colour:
                        visited[nr][nc] = True
                        q.append((nr, nc))

            rel_cells = [(rr - min_r, cc - min_c) for rr, cc in cells]
            width = max_c - min_c + 1
            height = max_r - min_r + 1
            comps.append({
                'colour': colour,
                'cells': rel_cells,
                'size': len(cells),
                'width': width,
                'height': height,
                'orig_tl': (min_r, min_c)   
            })

    comps.sort(key=lambda d: (d['size'], d['orig_tl']))

    out = [[dominant] * W for _ in range(H)]
    cur_col = 0                       

    for comp in comps:
        w, h = comp['width'], comp['height']

        if cur_col + w > W:
            break

        base_row = H - h                
        for dr, dc in comp['cells']:
            out[base_row + dr][cur_col + dc] = comp['colour']
        cur_col += w

    return out