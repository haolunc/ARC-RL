def transform(grid):

    R = len(grid)
    C = len(grid[0]) if R else 0

    rows = []
    cols = []
    for i in range(R):
        for j in range(C):
            if grid[i][j] != 0:
                rows.append(i)
                cols.append(j)

    if not rows:                     
        return [row[:] for row in grid]

    r0 = min(rows)                   
    c0 = min(cols)
    r_max = max(rows)
    c_max = max(cols)

    h = r_max - r0 + 1               
    w = c_max - c0 + 1               

    pattern = [row[c0:c0 + w] for row in grid[r0:r0 + h]]

    scales = []
    s = 2
    while r0 - (s - 1) >= 0:
        scales.append(s)
        s <<= 1                      

    total_width = w + sum(2 * s for s in scales)

    out = [[0] * total_width for _ in range(R)]

    def place(block, scale, r_start, c_start):

        for i in range(len(block)):
            for j in range(len(block[0])):
                val = block[i][j]
                if val == 0:
                    continue
                base_r = r_start + i * scale
                base_c = c_start + j * scale
                for dr in range(scale):
                    for dc in range(scale):
                        out[base_r + dr][base_c + dc] = val

    place(pattern, 1, r0, c0)

    cum_width = w                     
    for s in scales:
        c_start = c0 + cum_width
        r_start = r0 - (s - 1)
        place(pattern, s, r_start, c_start)
        cum_width += 2 * s

    return out