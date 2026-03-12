def transform(grid):

    h, w = len(grid), len(grid[0])

    rows_nonzero = [i for i in range(h) if any(cell != 0 for cell in grid[i])]
    cols_nonzero = [j for j in range(w) if any(grid[i][j] != 0 for i in range(h))]
    top, bottom = rows_nonzero[0], rows_nonzero[-1]
    left, right = cols_nonzero[0], cols_nonzero[-1]

    sub = [row[left:right + 1] for row in grid[top:bottom + 1]]
    H, W = len(sub), len(sub[0])

    border_color = sub[0][0]

    interior_rows = list(range(1, H - 1))
    interior_cols = list(range(1, W - 1))

    kept_rows = [r for r in interior_rows if any(sub[r][c] != 0 for c in interior_cols)]
    kept_cols = [c for c in interior_cols if any(sub[r][c] != 0 for r in interior_rows)]

    out_h = 2 + len(kept_rows) * 2
    out_w = 2 + len(kept_cols) * 2
    out = [[border_color for _ in range(out_w)] for _ in range(out_h)]

    for i, r in enumerate(kept_rows):
        for j, c in enumerate(kept_cols):
            colour = sub[r][c]
            if colour == 0:
                continue  

            tr = 1 + i * 2
            tc = 1 + j * 2
            out[tr][tc] = colour
            out[tr][tc + 1] = colour
            out[tr + 1][tc] = colour
            out[tr + 1][tc + 1] = colour

    return out