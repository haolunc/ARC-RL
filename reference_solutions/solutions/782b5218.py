def transform(grid):

    if not grid:
        return []

    R = len(grid)
    C = len(grid[0])

    result = [row[:] for row in grid]

    for j in range(C):

        col_vals = [grid[i][j] for i in range(R)]

        twos = [i for i, v in enumerate(col_vals) if v == 2]

        if not twos:                     
            for i in range(R):
                result[i][j] = 0
            continue

        top = min(twos)
        bottom = max(twos)

        freq = {}
        for v in col_vals:
            if v not in (0, 2):
                freq[v] = freq.get(v, 0) + 1
        if freq:
            dominant = max(freq.items(), key=lambda kv: kv[1])[0]
        else:
            dominant = 0

        for i in range(top):
            result[i][j] = 0

        for i in range(bottom + 1, R):
            result[i][j] = dominant

    return result