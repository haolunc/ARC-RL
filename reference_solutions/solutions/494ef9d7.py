def transform(grid):

    out = [row[:] for row in grid]

    target_sets = [{1, 8}, {4, 7}]

    for r, row in enumerate(out):

        nonzeros = [(c, v) for c, v in enumerate(row) if v != 0]

        if len(nonzeros) == 2:

            (c1, v1), (c2, v2) = sorted(nonzeros, key=lambda x: x[0])

            if {v1, v2} in target_sets:

                if c2 != c1 + 1:
                    out[r][c1 + 1] = v2          
                    out[r][c2] = 0               

    return out