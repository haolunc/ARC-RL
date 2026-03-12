def transform(grid):

    R = len(grid)
    C = len(grid[0]) if R else 0

    colours = {v for row in grid for v in row if v != 0}
    if len(colours) != 2:

        return [row[:] for row in grid]
    colour_A, colour_B = colours  

    def bbox(col):
        top = R
        bottom = -1
        left = C
        right = -1
        for i in range(R):
            for j in range(C):
                if grid[i][j] == col:
                    if i < top: top = i
                    if i > bottom: bottom = i
                    if j < left: left = j
                    if j > right: right = j
        return top, bottom, left, right

    ot, ob, ol, or_ = bbox(colour_A)
    it, ib, il, ir = bbox(colour_B)

    if not (ot <= it <= ib <= ob and ol <= il <= ir <= or_):
        colour_A, colour_B = colour_B, colour_A
        ot, ob, ol, or_ = it, ib, il, ir
        it, ib, il, ir = bbox(colour_B)  

    inner_h = ib - it + 1
    inner_w = ir - il + 1
    inner_thick = min(inner_h, inner_w)

    top_gap = ot
    left_gap = ol
    bottom_gap = R - 1 - ob
    right_gap = C - 1 - or_

    t = min(inner_thick, top_gap, left_gap, bottom_gap, right_gap)

    out = [row[:] for row in grid]

    for r in range(ot - t, ot):
        for c in range(ol - t, or_ + t + 1):
            out[r][c] = colour_B

    for r in range(ob + 1, ob + t + 1):
        for c in range(ol - t, or_ + t + 1):
            out[r][c] = colour_B

    for r in range(ot, ob + 1):
        for c in range(ol - t, ol):
            out[r][c] = colour_B
        for c in range(or_ + 1, or_ + t + 1):
            out[r][c] = colour_B

    return out