def transform(grid):

    h = len(grid)
    w = len(grid[0])

    from collections import Counter
    cnt = Counter()
    for row in grid:
        cnt.update(row)
    background = cnt.most_common(1)[0][0]

    colours = [c for c in cnt if c != background]
    if len(colours) != 2:

        return [list(row) for row in grid]

    A, B = colours

    def bounds(col):
        min_r, max_r = h, -1
        min_c, max_c = w, -1
        for r in range(h):
            for c in range(w):
                if grid[r][c] == col:
                    if r < min_r: min_r = r
                    if r > max_r: max_r = r
                    if c < min_c: min_c = c
                    if c > max_c: max_c = c
        return min_r, max_r, min_c, max_c

    a_min_r, a_max_r, a_min_c, a_max_c = bounds(A)
    b_min_r, b_max_r, b_min_c, b_max_c = bounds(B)

    rows_overlap = not (a_max_r < b_min_r or b_max_r < a_min_r)
    cols_overlap = not (a_max_c < b_min_c or b_max_c < a_min_c)

    out = [list(row) for row in grid]

    if rows_overlap:                     

        if a_min_c < b_min_c:
            left_col, left_min_c, left_max_c = A, a_min_c, a_max_c
            right_col, right_min_c, right_max_c = B, b_min_c, b_max_c
        else:
            left_col, left_min_c, left_max_c = B, b_min_c, b_max_c
            right_col, right_min_c, right_max_c = A, a_min_c, a_max_c

        gap = right_min_c - left_max_c - 1          
        expand = gap // 2

        left_start = left_max_c + 1
        left_end = left_max_c + expand          

        right_start = right_min_c - expand
        right_end = right_min_c - 1

        if gap % 2 == 0:

            pass

        for r in range(h):
            for c in range(left_start, left_end + 1):
                out[r][c] = left_col
            for c in range(right_start, right_end + 1):
                out[r][c] = right_col

    else:                                 

        if a_min_r < b_min_r:
            top_col, top_min_r, top_max_r = A, a_min_r, a_max_r
            bot_col, bot_min_r, bot_max_r = B, b_min_r, b_max_r
        else:
            top_col, top_min_r, top_max_r = B, b_min_r, b_max_r
            bot_col, bot_min_r, bot_max_r = A, a_min_r, a_max_r

        gap = bot_min_r - top_max_r - 1            
        expand = gap // 2

        top_start = top_max_r + 1
        top_end = top_max_r + expand                
        bot_start = bot_min_r - expand
        bot_end = bot_min_r - 1

        for r in range(top_start, top_end + 1):
            for c in range(w):
                out[r][c] = top_col
        for r in range(bot_start, bot_end + 1):
            for c in range(w):
                out[r][c] = bot_col

    return out