def transform(grid):

    result = []
    for row in grid:
        try:
            i1 = row.index(1)                     
            i8 = row.index(8, i1 + 1)             
        except ValueError:

            continue

        segment = row[i1 + 1 : i8]
        result.append(segment)
    return result