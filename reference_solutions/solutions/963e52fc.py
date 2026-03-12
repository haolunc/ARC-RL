def transform(grid):

    def minimal_period(row):

        n = len(row)
        for p in range(1, n + 1):
            ok = True
            for i in range(n):
                if row[i] != row[i % p]:
                    ok = False
                    break
            if ok:
                return p
        return n  

    out_grid = []
    for row in grid:
        n = len(row)
        p = minimal_period(row)
        pattern = row[:p]
        new_row = [pattern[i % p] for i in range(2 * n)]
        out_grid.append(new_row)
    return out_grid