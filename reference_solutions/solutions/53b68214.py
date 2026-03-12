def shift_row(row, s):

    w = len(row)
    new = [0] * w
    for i, v in enumerate(row):
        if v != 0:
            j = i + s
            if 0 <= j < w:
                new[j] = v
    return new

def find_period_and_shift(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    for k in range(1, h):
        shift = None
        ok = True
        for i in range(h - k):
            r1 = grid[i]
            r2 = grid[i + k]

            cols1 = [c for c, v in enumerate(r1) if v != 0]
            cols2 = [c for c, v in enumerate(r2) if v != 0]

            if not cols1 and not cols2:
                continue          
            if not cols1 or not cols2:
                ok = False
                break

            cand = cols2[0] - cols1[0]

            if shift_row(r1, cand) != r2:
                ok = False
                break

            if shift is None:
                shift = cand
            elif shift != cand:
                ok = False
                break

        if ok:
            if shift is None:
                shift = 0
            return k, shift

    return h, 0

def transform(grid):

    rows = [list(r) for r in grid]
    h = len(rows)

    if h == 10:
        return rows  

    k, s = find_period_and_shift(rows)

    out = rows[:]
    while len(out) < 10:
        src = out[len(out) - k]          
        out.append(shift_row(src, s))

    return out