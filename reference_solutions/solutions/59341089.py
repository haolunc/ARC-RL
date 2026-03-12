def transform(grid):

    out = []
    for row in grid:
        rev = row[::-1]               
        out_row = rev + row + rev + row
        out.append(out_row)
    return out