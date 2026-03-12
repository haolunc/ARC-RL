def transform(grid):

    freq = {}
    for row in grid:
        for v in row:
            freq[v] = freq.get(v, 0) + 1

    min_freq = min(freq.values())
    least_vals = {v for v, f in freq.items() if f == min_freq}

    out = [[0 for _ in range(9)] for _ in range(9)]

    for r in range(3):
        for c in range(3):
            if grid[r][c] in least_vals:
                for i in range(3):
                    for j in range(3):
                        out[r*3 + i][c*3 + j] = grid[i][j]
    return out