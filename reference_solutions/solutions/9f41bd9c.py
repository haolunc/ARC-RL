def transform(grid):

    H = len(grid)
    W = len(grid[0])

    C_up = grid[0][0]          
    C_low = grid[H - 1][0]     
    C_pat = 5                  

    rows_with_pat = set()
    cols_with_pat = set()
    for r in range(H):
        for c in range(W):
            if grid[r][c] == C_pat:
                rows_with_pat.add(r)
                cols_with_pat.add(c)

    if not rows_with_pat:          
        return [row[:] for row in grid]

    r0 = min(rows_with_pat)
    r1 = max(rows_with_pat)
    c0 = min(cols_with_pat)
    c1 = max(cols_with_pat)

    block_h = r1 - r0 + 1
    block_w = c1 - c0 + 1

    move_left = c0 > W // 2          

    out = [row[:] for row in grid]

    for r in range(r0, r0 + block_h):
        for c in range(c0, c0 + block_w):
            out[r][c] = C_up

    for i in range(block_h):
        shift = max(0, i - 2)
        if move_left:                         
            new_c = 0 + shift
        else:                                 
            new_c = (W - block_w) - shift

        src_r = r0 + i

        for j in range(block_w):
            out[src_r][new_c + j] = grid[src_r][c0 + j]

    row_9 = r0 + block_h
    if 0 <= row_9 < H:
        shift_for_9 = max(0, block_h - 2)
        if move_left:
            start = 0 + shift_for_9
            for c in range(start, W):
                out[row_9][c] = 9
        else:
            start = (W - block_w) - shift_for_9
            end = start + block_w          
            for c in range(0, end):
                out[row_9][c] = 9

    return out