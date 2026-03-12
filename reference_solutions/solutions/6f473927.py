def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    def comp(val):
        if val == 0:
            return 8
        if val == 2:
            return 0
        return 0

    comp_rev_row = lambda row: [comp(v) for v in row][::-1]

    comp_rows = [comp_rev_row(row) for row in grid]

    if grid and grid[0] and grid[0][0] == 0:
        left_block = grid
        right_block = comp_rows
    else:
        left_block = comp_rows
        right_block = grid

    out = [list(l + r) for l, r in zip(left_block, right_block)]
    return out