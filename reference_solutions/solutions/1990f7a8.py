def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0

    cells = [(r, c) for r in range(H) for c in range(W) if grid[r][c] == 2]
    if not cells:
        return [[0] * 7 for _ in range(7)]

    def biggest_gap(sorted_vals):

        best_gap = -1
        best_pos = None
        for i in range(len(sorted_vals) - 1):
            gap = sorted_vals[i + 1] - sorted_vals[i] - 1
            if gap > best_gap:
                best_gap = gap
                best_pos = sorted_vals[i] + 1      

        if best_pos is None:
            best_pos = sorted_vals[-1] + 1
        return best_pos

    rows = sorted({r for r, _ in cells})
    sep_row = biggest_gap(rows)

    top_rows = {r for r in rows if r < sep_row}
    bottom_rows = {r for r in rows if r > sep_row}

    def cols_of_rows(row_set):
        return sorted({c for r, c in cells if r in row_set})

    sep_col_top = biggest_gap(cols_of_rows(top_rows)) if top_rows else None
    sep_col_bottom = biggest_gap(cols_of_rows(bottom_rows)) if bottom_rows else None

    out = [[0] * 7 for _ in range(7)]

    def copy_subpattern(row_set, col_pred, row_off, col_off):
        sub = [(r, c) for (r, c) in cells if (r in row_set and col_pred(c))]
        if not sub:
            return
        min_r = min(r for r, _ in sub)
        min_c = min(c for _, c in sub)
        for r, c in sub:
            dr = r - min_r
            dc = c - min_c
            out[row_off + dr][col_off + dc] = 2

    if sep_col_top is not None:
        copy_subpattern(top_rows,
                        lambda c, sc=sep_col_top: c < sc,
                        0, 0)

        copy_subpattern(top_rows,
                        lambda c, sc=sep_col_top: c > sc,
                        0, 4)

    if sep_col_bottom is not None:
        copy_subpattern(bottom_rows,
                        lambda c, sc=sep_col_bottom: c < sc,
                        4, 0)
        copy_subpattern(bottom_rows,
                        lambda c, sc=sep_col_bottom: c > sc,
                        4, 4)

    return out