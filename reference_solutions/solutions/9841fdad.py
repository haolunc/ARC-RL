def transform(grid):

    from collections import Counter

    h = len(grid)
    w = len(grid[0])

    border = grid[0][0]

    sep = None
    for c in range(1, w - 1):
        if all(grid[r][c] == border for r in range(h)):
            sep = c
            break
    if sep is None:
        raise ValueError("Separator column not found")

    left_start = 1
    left_end = sep - 1
    right_start = sep + 1
    right_end = w - 2

    left_vals = [grid[r][c] for r in range(h) for c in range(left_start, left_end + 1)]
    background = Counter(left_vals).most_common(1)[0][0]

    out = [row[:] for row in grid]

    for r in range(h):
        c = left_start
        while c <= left_end:
            if out[r][c] != background:
                colour = out[r][c]
                seg_start = c
                while c <= left_end and out[r][c] == colour:
                    c += 1
                seg_end = c - 1

                d_left = seg_start - left_start
                d_right = left_end - seg_end

                if d_left < d_right:            
                    new_start = right_start + d_left
                    new_end = new_start + (seg_end - seg_start)
                elif d_right < d_left:          
                    new_end = right_end - d_right
                    new_start = new_end - (seg_end - seg_start)
                else:                           
                    new_start = right_start + 1
                    new_end = right_end - 1

                for cc in range(new_start, new_end + 1):
                    out[r][cc] = colour
            else:
                c += 1

    return out