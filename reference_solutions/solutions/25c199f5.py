def transform(grid):

    def block(col_start, col_end):
        return [row[col_start:col_end] for row in grid]

    left_block = block(0, 5)
    middle_block = block(6, 11)
    right_block = block(12, 17)

    rows = []
    for blk in (right_block, middle_block, left_block):
        for r in blk:
            if any(cell != 7 for cell in r):
                rows.append(r)

    while len(rows) < 5:
        rows.insert(0, [7] * 5)

    return rows[:5]