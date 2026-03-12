def transform(grid):

    out = [row[:] for row in grid]
    H = len(out)
    W = len(out[0])

    bottom = -1
    for r in range(H - 1, -1, -1):
        if any(cell != 0 for cell in out[r]):
            bottom = r
            break
    if bottom == -1:                     
        return out

    row_bottom = out[bottom]

    left = next(c for c, v in enumerate(row_bottom) if v != 0)

    outer_color = row_bottom[left]

    outer_width = 0
    for c in range(left, W):
        if row_bottom[c] == outer_color:
            outer_width += 1
        else:
            break

    inner_color = row_bottom[left + outer_width]

    start_row = bottom - outer_width - 1

    for k in range(outer_width):
        r = start_row + k
        if 0 <= r < H:
            out[r][k] = inner_color                
            out[r][W - 1 - k] = inner_color        

    return out