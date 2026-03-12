def transform(grid):

    out = [row[:] for row in grid]

    coloured = []
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v != 0:
                coloured.append((r, c, v))

    if not coloured:                     
        return out

    rows = [r for r, _, _ in coloured]
    cols = [c for _, c, _ in coloured]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)

    ctr_r = (min_r + max_r) // 2
    ctr_c = (min_c + max_c) // 2

    out[ctr_r][ctr_c] = 5

    def sgn(x):
        return (x > 0) - (x < 0)

    for r, c, val in coloured:
        dr = sgn(ctr_r - r)
        dc = sgn(ctr_c - c)

        if dr == 0 and dc == 0:
            continue

        nr, nc = r, c

        while (nr + dr != ctr_r) or (nc + dc != ctr_c):
            nr += dr
            nc += dc
        out[nr][nc] = val

    return out