def transform(grid):

    h = len(grid)
    w = len(grid[0])
    out = [row[:] for row in grid]

    from collections import Counter
    cnt = Counter()
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 0:
                cnt[v] += 1
    background = cnt.most_common(1)[0][0]

    zero_rows = []
    zero_cols = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0:
                zero_rows.append(r)
                zero_cols.append(c)
    zr0, zr1 = min(zero_rows), max(zero_rows)
    zc0, zc1 = min(zero_cols), max(zero_cols)

    pat_rows = []
    pat_cols = []
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 0 and v != background:
                pat_rows.append(r)
                pat_cols.append(c)
    pr0, pr1 = min(pat_rows), max(pat_rows)
    pc0, pc1 = min(pat_cols), max(pat_cols)

    for r in range(pr0, pr1 + 1):
        for c in range(pc0, pc1 + 1):

            mirrored_c = pc1 - (c - pc0)
            colour = grid[r][mirrored_c]

            tr = zr0 + (r - pr0)
            tc = zc0 + (c - pc0)

            if 0 <= tr < h and 0 <= tc < w:
                out[tr][tc] = colour

    return out