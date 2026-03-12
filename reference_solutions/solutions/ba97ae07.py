def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    colours = set()

    row_counts = {}

    col_counts = {}
    for i in range(h):
        for j in range(w):
            c = grid[i][j]
            if c == 0:
                continue
            colours.add(c)
            row_counts.setdefault(c, [0] * h)[i] += 1
            col_counts.setdefault(c, [0] * w)[j] += 1

    V = None
    vertical_cols = []
    for c in colours:
        col_cnt = col_counts.get(c, [])
        cols = [j for j, cnt in enumerate(col_cnt) if cnt >= h - 1]
        if cols:                     
            V = c
            vertical_cols = cols
            break                     
    if V is None:

        raise ValueError("Vertical colour not found")

    H = (colours - {V}).pop()

    horiz_rows = [i for i, cnt in enumerate(row_counts.get(H, [])) if cnt > 0]

    out = [row[:] for row in grid]          
    for i in horiz_rows:
        for j in vertical_cols:
            if out[i][j] == H:
                out[i][j] = V
            else:
                out[i][j] = H
    return out