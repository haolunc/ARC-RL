def transform(grid):

    R = len(grid)
    C = len(grid[0]) if R else 0

    from collections import Counter
    cnt = Counter()
    for row in grid:
        for v in row:
            if v != 0:
                cnt[v] += 1

    mask_colour, _ = cnt.most_common(1)[0]

    rows_mask = []
    cols_mask = []
    for i in range(R):
        for j in range(C):
            if grid[i][j] == mask_colour:
                rows_mask.append(i)
                cols_mask.append(j)
    r0, r1 = min(rows_mask), max(rows_mask)
    c0, c1 = min(cols_mask), max(cols_mask)
    mask_h = r1 - r0 + 1
    mask_w = c1 - c0 + 1

    candidate_rows = []
    for i in range(R):
        if any(grid[i][j] != 0 and grid[i][j] != mask_colour for j in range(C)):
            candidate_rows.append(i)

    patterns = []
    for i in candidate_rows:

        first = None
        last = None
        for j in range(C):
            v = grid[i][j]
            if v != 0 and v != mask_colour:
                if first is None:
                    first = j
                last = j
        if first is None:          
            continue
        slice_vals = [grid[i][j] for j in range(first, last + 1)]
        if slice_vals not in patterns:
            patterns.append(slice_vals)
        if len(patterns) == 2:
            break

    A, B = patterns[0], patterns[1]          

    out = []
    for i in range(mask_h):
        out_row = []
        for j in range(mask_w):
            if grid[r0 + i][c0 + j] == mask_colour:
                out_row.append(A[j])
            else:
                out_row.append(B[j])
        out.append(out_row)

    return out