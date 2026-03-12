def transform(grid):

    H = len(grid)
    W = len(grid[0])

    out = [[3 for _ in range(W)] for _ in range(H)]

    r, c = 1, 0
    out[r][c] = 0

    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    direction = 0  

    while True:
        moved = False
        for _ in range(4):          
            dr, dc = dirs[direction]
            nr, nc = r + dr, c + dc

            inside = (0 < nr < H - 1) and (0 < nc < W - 1)

            if inside and out[nr][nc] == 3:

                neighbours = 0
                for ar, ac in dirs:
                    ar, ac = nr + ar, nc + ac
                    if 0 <= ar < H and 0 <= ac < W and out[ar][ac] == 0:
                        neighbours += 1
                if neighbours == 1:          
                    out[nr][nc] = 0
                    r, c = nr, nc
                    moved = True
                    break                     

            direction = (direction + 1) % 4

        if not moved:               
            break

    return out