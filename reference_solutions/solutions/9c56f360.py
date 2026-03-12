def transform(grid):

    out = [list(row) for row in grid]

    for r in out:

        three_idx = [i for i, v in enumerate(r) if v == 3]
        if not three_idx:
            continue               

        rightmost = -1
        for i, v in enumerate(r):
            if v != 0 and v != 3:
                rightmost = i

        start = rightmost + 1

        for i in three_idx:
            r[i] = 0

        for offset, i in enumerate(range(start, start + len(three_idx))):
            if i < len(r):          
                r[i] = 3

    return out