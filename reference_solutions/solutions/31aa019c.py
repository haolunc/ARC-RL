def transform(grid):

    h = len(grid)
    w = len(grid[0])

    from collections import Counter
    cnt = Counter()
    pos = {}                     
    for i in range(h):
        for j in range(w):
            v = grid[i][j]
            if v != 0:
                cnt[v] += 1

                pos[v] = (i, j)

    unique_colour = None
    for colour, c in cnt.items():
        if c == 1:
            unique_colour = colour
            break

    if unique_colour is None:
        return [[0] * w for _ in range(h)]

    ci, cj = pos[unique_colour]

    out = [[0] * w for _ in range(h)]

    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            ni, nj = ci + di, cj + dj
            if 0 <= ni < h and 0 <= nj < w:
                out[ni][nj] = 2 if (di, dj) != (0, 0) else unique_colour

    return out