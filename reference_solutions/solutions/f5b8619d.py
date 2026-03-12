def transform(grid):

    h = len(grid)
    w = len(grid[0])

    col_has_nonzero = [any(grid[i][j] != 0 for i in range(h)) for j in range(w)]

    out_h, out_w = 2 * h, 2 * w
    out = [[0] * out_w for _ in range(out_h)]

    for i in range(out_h):
        for j in range(out_w):
            orig_val = grid[i % h][j % w]
            if orig_val == 0 and col_has_nonzero[j % w]:
                out[i][j] = 8
            else:
                out[i][j] = orig_val

    return out