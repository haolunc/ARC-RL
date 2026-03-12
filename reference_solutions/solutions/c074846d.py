def transform(grid):

    out = [row[:] for row in grid]
    h, w = len(grid), len(grid[0])

    for i in range(h):
        for j in range(w):
            if grid[i][j] == 5:
                r5, c5 = i, j
                break
        else:
            continue
        break

    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    line_cells = []
    dr, dc = 0, 0

    for d in dirs:
        rr, cc = r5 + d[0], c5 + d[1]
        if 0 <= rr < h and 0 <= cc < w and grid[rr][cc] == 2:
            dr, dc = d

            while 0 <= rr < h and 0 <= cc < w and grid[rr][cc] == 2:
                line_cells.append((rr, cc))
                rr += dr
                cc += dc
            break

    length = len(line_cells)

    for (r, c) in line_cells:
        out[r][c] = 3

    dr2, dc2 = dc, -dr

    for k in range(1, length + 1):
        nr, nc = r5 + dr2 * k, c5 + dc2 * k
        if 0 <= nr < h and 0 <= nc < w:
            out[nr][nc] = 2

    return out