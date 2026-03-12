def transform(grid):

    def dominant(line):

        freq = {}
        for v in line:
            freq[v] = freq.get(v, 0) + 1
        best_cnt = max(freq.values())
        return min(k for k, c in freq.items() if c == best_cnt)

    def runs(values):

        return 1 + sum(1 for i in range(1, len(values)) if values[i] != values[i-1])

    H = len(grid)          
    W = len(grid[0]) if H else 0   

    col_major = []
    for c in range(W):
        column = [grid[r][c] for r in range(H)]
        col_major.append(dominant(column))

    row_major = [dominant(row) for row in grid]

    if runs(col_major) <= runs(row_major):

        out = [[col_major[c] for c in range(W)] for _ in range(H)]
    else:

        out = [[row_major[r] for _ in range(W)] for r in range(H)]

    return out