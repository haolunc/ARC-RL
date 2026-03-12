def transform(grid):

    g = [row[:] for row in grid]
    n = len(g)

    diag_indices = [i for i in range(n) if g[i][i] == 1]
    if len(diag_indices) >= 2:
        d = diag_indices[1] - diag_indices[0]
        last = diag_indices[-1]
        pos = last + d
        while pos < n:
            if g[pos][pos] == 0:
                g[pos][pos] = 2
            pos += d
    return g