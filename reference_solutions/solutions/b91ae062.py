def transform(grid):

    distinct = {v for row in grid for v in row if v != 0}
    N = len(distinct)
    if N == 0:          
        N = 1

    expanded = []
    for row in grid:

        for _ in range(N):
            new_row = []
            for val in row:

                new_row.extend([val] * N)
            expanded.append(new_row)
    return expanded