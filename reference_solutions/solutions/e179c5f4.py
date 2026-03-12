def transform(grid):

    W = len(grid)
    if W == 0:
        return []
    H = len(grid[0])

    start_row = 0
    found = False
    last_col = grid[W - 1]
    for i in range(H):
        if last_col[i] == 1:
            start_row = i
            found = True
            break
    if not found:

        start_row = 0

    out = [[8 for _ in range(H)] for _ in range(W)]

    r = start_row
    dir = 1 if H <= 1 or start_row < H - 1 else -1  

    for j in range(W - 1, -1, -1):
        out[j][r] = 1
        if j == 0:
            break

        if r + dir > H - 1 or r + dir < 0:
            dir = -dir
        r = r + dir

    return out