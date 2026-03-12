def transform(grid):

    H = len(grid)          
    W = len(grid[0])       

    pattern = []
    for c in range(W):
        pat = tuple(1 if grid[r][c] == 8 else 0 for r in range(H))
        pattern.append(pat)

    zones = []          
    i = 0
    while i < W:
        if any(pattern[i]):          
            j = i + 1
            while j < W and pattern[j] == pattern[i]:
                j += 1
            zones.append((i, j, pattern[i]))
            i = j
        else:
            i += 1

    source_cols = []    
    for c in range(W):

        col_vals = [grid[r][c] for r in range(H) if grid[r][c] not in (0, 8)]
        if col_vals:

            colour = col_vals[0]
            source_cols.append((c, colour))

    source_cols.sort(key=lambda x: x[0])

    mapping = []   
    for (src_idx, (src_col, colour)), zone in zip(enumerate(source_cols), zones):
        start, end, pat = zone
        mapping.append((colour, start, end, pat))

    out = [[0] * W for _ in range(H)]

    for colour, c_start, c_end, pat in mapping:
        for c in range(c_start, c_end):
            for r in range(H):
                if pat[r] == 1:          
                    out[r][c] = colour

    return out