def transform(grid):

    from collections import Counter

    h = len(grid)
    w = len(grid[0])

    dominant = []
    for c in range(w):
        col_vals = [grid[r][c] for r in range(h)]
        cnt = Counter(col_vals)

        dominant.append(cnt.most_common(1)[0][0])

    blocks = []
    cur = [0]
    for c in range(1, w):
        if dominant[c] == dominant[c - 1]:
            cur.append(c)
        else:
            blocks.append(cur)
            cur = [c]
    blocks.append(cur)

    block_dom = [dominant[blk[0]] for blk in blocks]
    increasing = all(block_dom[i] < block_dom[i + 1] for i in range(len(block_dom) - 1))

    if increasing:
        new_order = list(reversed(blocks))
    else:
        new_order = blocks[1:] + [blocks[0]]

    out = [[0] * w for _ in range(h)]
    out_col = 0
    for blk in new_order:
        for c in blk:                     
            for r in range(h):
                out[r][out_col] = grid[r][c]
            out_col += 1

    return out