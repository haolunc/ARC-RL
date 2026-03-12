def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for i in range(h):
        for j in range(w):
            if grid[i][j] == 0:

                has_zero_neighbor = False
                for di, dj in dirs:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < h and 0 <= nj < w:
                        if grid[ni][nj] == 0:
                            has_zero_neighbor = True
                            break
                if has_zero_neighbor:
                    out[i][j] = 8   

    return out