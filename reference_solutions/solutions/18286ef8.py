def transform(grid):
    import copy
    from collections import Counter

    h = len(grid)
    w = len(grid[0])

    pos6 = pos9 = None
    for i in range(h):
        for j in range(w):
            v = grid[i][j]
            if v == 6:
                pos6 = (i, j)
            elif v == 9:
                pos9 = (i, j)

    if pos6 is None or pos9 is None:
        return copy.deepcopy(grid)

    zero_rows = [i for i in range(h) if all(grid[i][j] == 0 for j in range(w))]
    zero_cols = [j for j in range(w) if all(grid[i][j] == 0 for i in range(h))]

    def block_info(r, c):

        row_band = sum(1 for zr in zero_rows if zr < r)

        col_band = sum(1 for zc in zero_cols if zc < c)

        next_zero_row = next((zr for zr in zero_rows if zr > r), h)
        prev_zero_row = -1
        for zr in reversed(zero_rows):
            if zr < r:
                prev_zero_row = zr
                break
        r_min = prev_zero_row + 1
        r_max = next_zero_row - 1

        next_zero_col = next((zc for zc in zero_cols if zc > c), w)
        prev_zero_col = -1
        for zc in reversed(zero_cols):
            if zc < c:
                prev_zero_col = zc
                break
        c_min = prev_zero_col + 1
        c_max = next_zero_col - 1

        return row_band, col_band, r_min, r_max, c_min, c_max

    b9 = block_info(*pos9)
    b6 = block_info(*pos6)

    _, _, r_min, r_max, c_min, c_max = b9
    row_band9, col_band9, _, _, _, _ = b9
    row_band6, col_band6, _, _, _, _ = b6

    if row_band6 < row_band9:          
        target_r = r_min
    elif row_band6 > row_band9:        
        target_r = r_max
    else:                              
        target_r = pos9[0]

    if col_band6 < col_band9:          
        target_c = c_min
    elif col_band6 > col_band9:        
        target_c = c_max
    else:                              
        target_c = pos9[1]

    colours = []
    for i in range(r_min, r_max + 1):
        for j in range(c_min, c_max + 1):
            val = grid[i][j]
            if val != 0:
                colours.append(val)
    bg = Counter(colours).most_common(1)[0][0]

    out = copy.deepcopy(grid)

    out[pos6[0]][pos6[1]] = 9

    out[pos9[0]][pos9[1]] = bg

    if (target_r, target_c) != pos6 and (target_r, target_c) != pos9:
        out[target_r][target_c] = 9

    return out