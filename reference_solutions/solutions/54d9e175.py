def transform(grid):

    out = [row[:] for row in grid]

    R = len(out)
    C = len(out[0]) if R else 0

    sep_rows = [r for r in range(R) if all(out[r][c] == 5 for c in range(C))]

    sep_cols = [c for c in range(C) if all(out[r][c] == 5 for r in range(R))]

    def intervals_between(start, end, separators):
        intervals = []
        prev = start - 1
        for s in separators:
            if s - prev > 1:
                intervals.append((prev + 1, s - 1))
            prev = s
        if end - prev >= 1:
            intervals.append((prev + 1, end))
        return intervals

    row_intervals = intervals_between(0, R - 1, sep_rows)
    col_intervals = intervals_between(0, C - 1, sep_cols)

    for r0, r1 in row_intervals:
        for c0, c1 in col_intervals:

            rc = (r0 + r1) // 2
            cc = (c0 + c1) // 2
            centre_val = out[rc][cc]
            if centre_val != 0:          
                new_val = centre_val + 5
                for r in range(r0, r1 + 1):
                    for c in range(c0, c1 + 1):
                        out[r][c] = new_val
    return out