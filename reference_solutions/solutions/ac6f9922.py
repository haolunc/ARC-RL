def transform(grid):

    h = len(grid)
    w = len(grid[0])

    border_color = grid[0][0]

    from collections import Counter, deque

    interior_counts = Counter()
    for i in range(1, h-1):
        for j in range(1, w-1):
            c = grid[i][j]
            if c != border_color:
                interior_counts[c] += 1

    if interior_counts:
        background_color = interior_counts.most_common(1)[0][0]
    else:
        background_color = border_color   

    visited = [[False]*w for _ in range(h)]
    components = []                     

    for i in range(1, h-1):
        for j in range(1, w-1):
            if visited[i][j]:
                continue
            colour = grid[i][j]
            if colour == border_color or colour == background_color:
                continue

            q = deque()
            q.append((i, j))
            visited[i][j] = True
            min_r, min_c = i, j
            while q:
                r, c = q.popleft()

                if r < min_r: min_r = r
                if c < min_c: min_c = c

                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc]:
                        if grid[nr][nc] == colour:
                            visited[nr][nc] = True
                            q.append((nr, nc))
            components.append((min_r, min_c, colour))

    rows_set = sorted({r for r, _, _ in components})
    cols_set = sorted({c for _, c, _ in components})

    out_rows = max(2, len(rows_set))
    out_cols = max(2, len(cols_set))

    row_index = {r: idx for idx, r in enumerate(rows_set)}
    col_index = {c: idx for idx, c in enumerate(cols_set)}

    out_grid = [[border_color for _ in range(out_cols)] for _ in range(out_rows)]

    for r, c, col in components:
        ri = row_index[r]
        ci = col_index[c]
        out_grid[ri][ci] = col

    return out_grid