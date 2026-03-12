def transform(grid):

    rows = len(grid)
    cols = len(grid[0])

    separator = None
    for c in range(cols):
        col_vals = [grid[r][c] for r in range(rows)]

        if col_vals and col_vals[0] != 0 and all(v == col_vals[0] for v in col_vals):
            separator = c
            break
    if separator is None:

        separator = cols // 2

    left = [row[:separator] for row in grid]          
    right = [row[separator + 1:] for row in grid]    

    width = len(left[0])

    out = []
    for r in range(rows):
        out_row = []
        for c in range(width):
            l = left[r][c]
            rgt = right[r][c]
            if l != 0 and rgt != 0:
                out_row.append(l)          
            elif l != 0:
                out_row.append(2)          
            elif rgt != 0:
                out_row.append(1)          
            else:
                out_row.append(0)          
        out.append(out_row)

    return out