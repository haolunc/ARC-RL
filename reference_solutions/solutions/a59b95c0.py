def transform(grid):

    n = len(grid)

    distinct = set()
    for row in grid:
        distinct.update(row)
    k = len(distinct)          

    out = []
    for _ in range(k):                 
        for row in grid:
            new_row = []
            for _ in range(k):         
                new_row.extend(row)
            out.append(new_row)

    return out