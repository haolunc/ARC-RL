def transform(grid):

    g = [list(row) for row in grid]
    h = len(g)
    w = len(g[0]) if h else 0

    five_cells = [(i, j) for i in range(h) for j in range(w) if g[i][j] == 5]
    if not five_cells:          
        return grid

    min_r = min(i for i, _ in five_cells)
    max_r = max(i for i, _ in five_cells)
    min_c = min(j for _, j in five_cells)
    max_c = max(j for _, j in five_cells)

    vertical = (max_r - min_r) >= (max_c - min_c)   

    if vertical:

        for i in range(h):

            right_cnt = sum(1 for j in range(max_c + 1, w)
                            if g[i][j] not in (0, 5))
            left_cnt  = sum(1 for j in range(0, min_c)
                            if g[i][j] not in (0, 5))

            for j in range(max_c + 1, w):
                if g[i][j] not in (0, 5):
                    g[i][j] = 0
            for j in range(0, min_c):
                if g[i][j] not in (0, 5):
                    g[i][j] = 0

            for k in range(right_cnt):
                col = max_c + 1 + k
                if col < w:
                    g[i][col] = 5

            for k in range(left_cnt):
                col = min_c - 1 - k
                if col >= 0:
                    g[i][col] = 5

    else:

        for j in range(w):

            below_cnt = sum(1 for i in range(max_r + 1, h)
                            if g[i][j] not in (0, 5))
            above_cnt = sum(1 for i in range(0, min_r)
                            if g[i][j] not in (0, 5))

            for i in range(max_r + 1, h):
                if g[i][j] not in (0, 5):
                    g[i][j] = 0
            for i in range(0, min_r):
                if g[i][j] not in (0, 5):
                    g[i][j] = 0

            for k in range(below_cnt):
                row = max_r + 1 + k
                if row < h:
                    g[row][j] = 5

            for k in range(above_cnt):
                row = min_r - 1 - k
                if row >= 0:
                    g[row][j] = 5

    return g