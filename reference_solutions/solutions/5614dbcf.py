def transform(grid):

    n = len(grid)                 
    if n == 0:
        return []

    block_size = n // 3           

    out = []
    for bi in range(3):           
        row = []
        r0 = bi * block_size
        for bj in range(3):       
            c0 = bj * block_size

            freq = {}
            for i in range(r0, r0 + block_size):
                for j in range(c0, c0 + block_size):
                    col = grid[i][j]
                    freq[col] = freq.get(col, 0) + 1

            dominant = max(freq.items(), key=lambda kv: kv[1])[0]
            row.append(dominant)
        out.append(row)

    return out