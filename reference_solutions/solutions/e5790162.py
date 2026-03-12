def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0

    start = None
    for i in range(H):
        for j in range(W):
            if grid[i][j] == 3:
                start = (i, j)
                break
        if start:
            break
    if not start:
        return grid  

    r, c = start

    dr, dc = 0, 1

    while True:
        nr = r + dr
        nc = c + dc

        if not (0 <= nr < H and 0 <= nc < W):
            break

        nxt = grid[nr][nc]

        if nxt == 0:                     
            r, c = nr, nc
            grid[r][c] = 3
            continue

        if nxt == 6:                     
            dr, dc = dc, -dr
        else:                            
            dr, dc = -dc, dr

    return grid