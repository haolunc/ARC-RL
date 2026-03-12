def transform(grid):

    result = []
    for row in grid:
        out_row = []
        for c in range(4):          
            left_colored  = row[c] != 0
            right_colored = row[c + 5] != 0
            out_row.append(2 if left_colored ^ right_colored else 0)
        result.append(out_row)
    return result