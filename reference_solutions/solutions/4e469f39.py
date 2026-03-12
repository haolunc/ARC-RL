def transform(grid):

    from collections import deque

    h = len(grid)
    w = len(grid[0])

    out = [row[:] for row in grid]

    visited = [[False] * w for _ in range(h)]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 5 and not visited[r][c]:

                comp = []
                q = deque([(r, c)])
                visited[r][c] = True
                while q:
                    cr, cc = q.popleft()
                    comp.append((cr, cc))
                    for dr, dc in dirs:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < h and 0 <= nc < w                                and grid[nr][nc] == 5 and not visited[nr][nc]:
                            visited[nr][nc] = True
                            q.append((nr, nc))

                rows = [p[0] for p in comp]
                cols = [p[1] for p in comp]
                min_r, max_r = min(rows), max(rows)
                min_c, max_c = min(cols), max(cols)

                top_row = min_r
                five_cols_top = sorted(c for (rr, c) in comp if rr == top_row)
                gap_c = None
                for i in range(len(five_cols_top) - 1):
                    if five_cols_top[i + 1] - five_cols_top[i] == 2:

                        gap_c = five_cols_top[i] + 1
                        break
                if gap_c is None:

                    continue

                out[top_row][gap_c] = 2

                for rr in range(min_r + 1, max_r):
                    for cc in range(min_c + 1, max_c):
                        out[rr][cc] = 2

                above = top_row - 1
                if above >= 0:

                    left_interior = min_c + 1          
                    right_interior = max_c - 1         
                    if gap_c == left_interior:
                        step = 1                     
                    else:
                        step = -1                    

                    cc = gap_c
                    while 0 <= cc < w:
                        out[above][cc] = 2
                        cc += step

    return out