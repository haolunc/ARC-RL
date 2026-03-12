def transform(grid):

    from collections import Counter

    h = len(grid)
    w = len(grid[0]) if h else 0

    eight_pos = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 8]
    if not eight_pos:
        return grid

    four_cols = [c for r in range(h) for c in range(w) if grid[r][c] == 8]  

    four_cols = [c for r in range(h) for c in range(w) if grid[r][c] == 4]
    if four_cols:
        cnt = Counter(four_cols)
        c_ref = cnt.most_common(1)[0][0]
    else:

        c_ref = w // 2

    left_cnt = sum(1 for _, c in eight_pos if c < c_ref)
    right_cnt = sum(1 for _, c in eight_pos if c >= c_ref)

    if left_cnt > right_cnt:

        c_max = max(c for _, c in eight_pos)
        for r, c in eight_pos:
            c2 = 2 * c_max + 1 - c
            if 0 <= c2 < w:
                grid[r][c2] = 8
    else:

        c_min = min(c for _, c in eight_pos)
        for r, c in eight_pos:
            c2 = 2 * c_min - 1 - c
            if 0 <= c2 < w:
                grid[r][c2] = 8

    return grid