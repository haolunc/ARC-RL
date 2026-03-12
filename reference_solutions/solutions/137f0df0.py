def transform(grid):

    h = len(grid)
    w = len(grid[0])
    out = [row[:] for row in grid]

    block_rows = set()
    block_cols = set()
    for r in range(h):
        for c in range(w):
            if grid[r][c] != 0:
                block_rows.add(r)
                block_cols.add(c)

    if not block_rows or not block_cols:
        return out   

    min_r, max_r = min(block_rows), max(block_rows)
    min_c, max_c = min(block_cols), max(block_cols)

    gap_rows = {r for r in range(min_r, max_r + 1) if r not in block_rows}
    gap_cols = {c for c in range(min_c, max_c + 1) if c not in block_cols}

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 0:
                continue          

            if min_r <= r <= max_r and min_c <= c <= max_c:
                out[r][c] = 2
            else:

                if (r < min_r or r > max_r) and (c in gap_cols):
                    out[r][c] = 1
                elif (c < min_c or c > max_c) and (r in gap_rows):
                    out[r][c] = 1

    return out