def transform(grid):

    h = len(grid)
    w = len(grid[0])

    rows = [i for i in range(h) for j in range(w) if grid[i][j] == 2]
    cols = [j for i in range(h) for j in range(w) if grid[i][j] == 2]

    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)

    out = [row[:] for row in grid]

    for i in range(h):
        for j in range(w):
            v = grid[i][j]
            if v != 0 and v != 2:

                out[i][j] = 0

                if i < min_r:
                    new_i = min_r + (min_r - i)
                elif i > max_r:
                    new_i = max_r - (i - max_r)
                else:
                    new_i = i

                if j < min_c:
                    new_j = min_c + (min_c - j)
                elif j > max_c:
                    new_j = max_c - (j - max_c)
                else:
                    new_j = j

                out[new_i][new_j] = v

    return out