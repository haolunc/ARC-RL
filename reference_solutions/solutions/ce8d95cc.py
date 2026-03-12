def transform(grid):

    compressed_rows = []
    for row in grid:
        if not compressed_rows or row != compressed_rows[-1]:
            compressed_rows.append(row)

    transposed = list(zip(*compressed_rows))          
    compressed_cols = []
    for col in transposed:
        if not compressed_cols or col != compressed_cols[-1]:
            compressed_cols.append(col)

    result = [list(r) for r in zip(*compressed_cols)]
    return result