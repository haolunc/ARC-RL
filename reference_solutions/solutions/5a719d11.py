def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h>0 else 0

    def row_all_zero(r):
        return all(grid[r][c]==0 for c in range(w))
    def col_all_zero(c):
        return all(grid[r][c]==0 for r in range(h))

    row_nonzero_flags = [not row_all_zero(r) for r in range(h)]
    row_segments = []
    r = 0
    while r < h:
        if row_nonzero_flags[r]:
            start = r
            while r < h and row_nonzero_flags[r]:
                r += 1
            row_segments.append((start, r))  
        else:
            r += 1

    col_nonzero_flags = [not col_all_zero(c) for c in range(w)]
    col_segments = []
    c = 0
    while c < w:
        if col_nonzero_flags[c]:
            start = c
            while c < w and col_nonzero_flags[c]:
                c += 1
            col_segments.append((start, c))
        else:
            c += 1

    out = [row[:] for row in grid]

    if len(col_segments) < 2 or len(row_segments) < 1:
        return out  

    left_idx = 0
    right_idx = len(col_segments)-1

    for br in range(len(row_segments)):
        r0, r1 = row_segments[br]

        cl0, cl1 = col_segments[left_idx]
        cr0, cr1 = col_segments[right_idx]
        bh = r1 - r0
        bw_left = cl1 - cl0
        bw_right = cr1 - cr0

        h_use = min(bh, bh)
        w_use = min(bw_left, bw_right)

        from collections import Counter
        cnt_left = Counter()
        cnt_right = Counter()
        for i in range(r0, r0+h_use):
            for j in range(cl0, cl0+w_use):
                v = grid[i][j]
                if v != 0:
                    cnt_left[v] += 1
            for j in range(cr0, cr0+w_use):
                v = grid[i][j]
                if v != 0:
                    cnt_right[v] += 1

        def dominant(counter):
            if not counter:
                return 0
            return max(counter.items(), key=lambda x: x[1])[0]
        dom_left = dominant(cnt_left)
        dom_right = dominant(cnt_right)

        mask_left = [[False]*w_use for _ in range(h_use)]
        mask_right = [[False]*w_use for _ in range(h_use)]
        for i in range(h_use):
            for j in range(w_use):
                vL = grid[r0+i][cl0+j]
                vR = grid[r0+i][cr0+j]
                if vL != 0 and vL != dom_left:
                    mask_left[i][j] = True
                if vR != 0 and vR != dom_right:
                    mask_right[i][j] = True

        for i in range(h_use):
            for j in range(w_use):
                out[r0+i][cl0+j] = dom_left
                out[r0+i][cr0+j] = dom_right
        for i in range(h_use):
            for j in range(w_use):
                if mask_right[i][j]:
                    out[r0+i][cl0+j] = dom_right
                if mask_left[i][j]:
                    out[r0+i][cr0+j] = dom_left

    return out