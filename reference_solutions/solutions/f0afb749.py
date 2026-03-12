def transform(grid):

    n = len(grid)                 
    m = len(grid[0])
    H, W = 2 * n, 2 * m           

    out = [[0] * W for _ in range(H)]

    offsets = set()
    for i in range(n):
        for j in range(m):
            v = grid[i][j]
            if v != 0:

                out[2 * i][2 * j] = v
                out[2 * i][2 * j + 1] = v
                out[2 * i + 1][2 * j] = v
                out[2 * i + 1][2 * j + 1] = v

                offsets.add(2 * (i - j))

    for d in offsets:
        for r in range(H):
            c = r - d
            if 0 <= c < W and out[r][c] == 0:
                out[r][c] = 1

    return out