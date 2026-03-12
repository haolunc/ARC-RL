def transform(grid):

    h = len(grid)
    w = len(grid[0])

    sep = [c for c in range(w) if all(grid[r][c] == 5 for r in range(h))]

    bounds = [-1] + sep + [w]
    regions = []
    for i in range(len(bounds) - 1):
        left = bounds[i] + 1
        right = bounds[i + 1]
        if left < right:
            sub = [row[left:right] for row in grid]
            regions.append(sub)          

    pattern_masks = []   
    block_colours = []   
    N = None

    for reg in regions:

        nz = [(r, c) for r in range(len(reg))
                     for c in range(len(reg[0])) if reg[r][c] != 0]

        if not nz:          
            continue

        min_r = min(r for r, _ in nz)
        max_r = max(r for r, _ in nz)
        min_c = min(c for _, c in nz)
        max_c = max(c for _, c in nz)

        hbox = max_r - min_r + 1
        wbox = max_c - min_c + 1

        box = [[reg[r][c] for c in range(min_c, max_c + 1)]
               for r in range(min_r, max_r + 1)]

        colours = {v for row in box for v in row if v != 0}

        if len(colours) == 1 and all(v != 0 for row in box for v in row):
            block_colours.append(next(iter(colours)))
            if N is None:
                N = hbox      
        else:   

            mask = [[1 if v != 0 else 0 for v in row] for row in box]
            pattern_masks.append(mask)

    A, B = pattern_masks[0], pattern_masks[1]   
    C, D = block_colours[0], block_colours[1]   

    out_size = N * N
    out = [[0] * out_size for _ in range(out_size)]

    for br in range(N):          
        for bc in range(N):      
            uniform = (B[br][bc] == 0)
            for i in range(N):
                for j in range(N):
                    if uniform:
                        out[br * N + i][bc * N + j] = D
                    else:
                        out[br * N + i][bc * N + j] = C if A[i][j] else D

    return out