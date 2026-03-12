def transform(grid):

    distinct = {v for row in grid for v in row if v != 0}
    k = len(distinct)

    if k == 0:
        return []

    h, w = len(grid), len(grid[0])
    out_h, out_w = h * k, w * k

    out = [[0] * out_w for _ in range(out_h)]

    for i in range(h):
        for j in range(w):
            val = grid[i][j]

            for di in range(k):
                for dj in range(k):
                    out[i * k + di][j * k + dj] = val
    return out