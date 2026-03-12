def transform(input_grid):

    v = input_grid[0]
    L = len(v)

    k = sum(1 for x in v if x != 0)

    N = L * k

    out = [[0 for _ in range(N)] for _ in range(N)]

    for r in range(N):
        c_start = N - 1 - r
        for i, val in enumerate(v):
            c = c_start + i
            if 0 <= c < N:
                out[r][c] = val

    return out