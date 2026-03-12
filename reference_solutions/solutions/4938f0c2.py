def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    rows3 = [r for r in range(h) for c in range(w) if grid[r][c] == 3]
    cols3 = [c for c in range(w) for r in range(h) if grid[r][c] == 3]

    if not rows3 or not cols3:
        return [row[:] for row in grid]

    block_top = min(rows3)
    block_bottom = max(rows3)
    block_left = min(cols3)
    block_right = max(cols3)

    out = [row[:] for row in grid]

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 2:
                continue

            c_h = block_left + block_right - c

            r_v = block_top + block_bottom - r

            out[r][c_h] = 2          
            out[r_v][c] = 2          
            out[r_v][c_h] = 2        

    return out