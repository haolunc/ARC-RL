def transform(grid):

    H = len(grid)
    W = len(grid[0])

    out = [[0 for _ in range(W)] for _ in range(H)]
    visited = [[False] * W for _ in range(H)]

    for r in range(H):
        for c in range(W):
            if grid[r][c] == 5 and not visited[r][c]:

                r0 = r
                while r0 - 1 >= 0 and grid[r0 - 1][c] == 5:
                    r0 -= 1
                c0 = c
                while c0 - 1 >= 0 and grid[r][c0 - 1] == 5:
                    c0 -= 1

                r1 = r0
                while True:
                    nxt = r1 + 1
                    if nxt >= H:
                        break
                    if all(grid[nxt][j] == 5 for j in range(c0, c0 + (c - c0 + 1))):
                        r1 = nxt
                    else:
                        break

                c1 = c0
                while True:
                    nxt = c1 + 1
                    if nxt >= W:
                        break
                    if all(grid[i][nxt] == 5 for i in range(r0, r0 + (r - r0 + 1))):
                        c1 = nxt
                    else:
                        break

                for i in range(r0, r1 + 1):
                    for j in range(c0, c1 + 1):
                        visited[i][j] = True

                tl = grid[r0 - 1][c0 - 1]
                tr = grid[r0 - 1][c1 + 1]
                bl = grid[r1 + 1][c0 - 1]
                br = grid[r1 + 1][c1 + 1]

                out[r0 - 1][c0 - 1] = 0
                out[r0 - 1][c1 + 1] = 0
                out[r1 + 1][c0 - 1] = 0
                out[r1 + 1][c1 + 1] = 0

                h = r1 - r0 + 1
                w = c1 - c0 + 1
                hh = h // 2
                ww = w // 2

                for i in range(r0, r0 + hh):
                    for j in range(c0, c0 + ww):
                        out[i][j] = tl
                    for j in range(c0 + ww, c1 + 1):
                        out[i][j] = tr
                for i in range(r0 + hh, r1 + 1):
                    for j in range(c0, c0 + ww):
                        out[i][j] = bl
                    for j in range(c0 + ww, c1 + 1):
                        out[i][j] = br

    return out