def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    filled = set()
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 8:
                filled.add((r, c))

    decorations = set()  

    changed = True
    while changed:
        changed = False
        new_add = set()

        for r in range(h):
            for c in range(w):
                if (r, c) in filled:
                    continue
                if grid[r][c] != 0 and grid[r][c] != 0:  

                    continue

                cond1 = (r+1 < h and c-1 >= 0 and c+1 < w and
                         ((r+1, c-1) in filled) and ((r+1, c+1) in filled))

                cond2 = (r-1 >= 0 and c-1 >= 0 and c+1 < w and
                         ((r-1, c-1) in filled) and ((r-1, c+1) in filled))

                cond3 = (r-1 >= 0 and r+1 < h and c-1 >= 0 and
                         ((r-1, c-1) in filled) and ((r+1, c-1) in filled))

                cond4 = (r-1 >= 0 and r+1 < h and c+1 < w and
                         ((r-1, c+1) in filled) and ((r+1, c+1) in filled))

                if cond1 or cond2 or cond3 or cond4:

                    if (r, c) not in decorations and (r, c) not in filled:
                        new_add.add((r, c))

        if new_add:
            changed = True

            for cell in new_add:
                decorations.add(cell)
                filled.add(cell)

    out = [row[:] for row in grid]
    for (r, c) in decorations:

        if out[r][c] == 8:
            continue
        out[r][c] = 4
    return out