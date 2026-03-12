def transform(grid):

    n = len(grid)                     

    freq = {}
    for row in grid:
        for c in row:
            freq[c] = freq.get(c, 0) + 1

    mode = max(freq, key=freq.get)

    big_n = n * n
    out = [[0] * big_n for _ in range(big_n)]

    for i in range(n):
        for j in range(n):
            if grid[i][j] == mode:

                for p in range(n):
                    for q in range(n):
                        out[i * n + p][j * n + q] = grid[p][q]

    return out