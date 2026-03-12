def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0

    visited = [[False] * W for _ in range(H)]
    shapes = []                     

    from collections import deque

    for r in range(H):
        for c in range(W):
            if grid[r][c] != 0 and not visited[r][c]:
                colour = grid[r][c]
                cells = []
                q = deque()
                q.append((r, c))
                visited[r][c] = True
                while q:
                    cr, cc = q.popleft()
                    cells.append((cr, cc))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < H and 0 <= nc < W:
                            if not visited[nr][nc] and grid[nr][nc] == colour:
                                visited[nr][nc] = True
                                q.append((nr, nc))
                max_col = max(c for (_, c) in cells)
                shapes.append((colour, cells, max_col))

    shapes.sort(key=lambda s: s[2], reverse=True)

    out = [[0] * W for _ in range(H)]

    for colour, cells, _ in shapes:
        best_shift = 0

        for shift in range(1, W):
            ok = True
            for r, c in cells:
                nc = c + shift
                if nc >= W or out[r][nc] != 0:
                    ok = False
                    break
            if ok:
                best_shift = shift
            else:
                break      

        for r, c in cells:
            out[r][c + best_shift] = colour

    return out