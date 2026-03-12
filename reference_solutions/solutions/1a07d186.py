def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0

    out = [[0] * W for _ in range(H)]

    line_info = {}                     

    for r in range(H):
        c = grid[r][0]
        if c == 0:
            continue
        if all(grid[r][k] == c for k in range(W)):
            line_info[c] = ('h', r)

    for col in range(W):
        c = grid[0][col]
        if c == 0:
            continue
        if all(grid[r][col] == c for r in range(H)):
            line_info[c] = ('v', col)

    for colour, (orient, idx) in line_info.items():
        if orient == 'h':          
            out[idx] = [colour] * W
        else:                     
            for r in range(H):
                out[r][idx] = colour

    for r in range(H):
        for c in range(W):
            colour = grid[r][c]
            if colour == 0:
                continue
            if colour not in line_info:
                continue          

            orient, idx = line_info[colour]

            if (orient == 'h' and r == idx) or (orient == 'v' and c == idx):
                continue

            if orient == 'h':
                new_r = idx - 1 if r < idx else idx + 1
                new_c = c
            else:  
                new_c = idx - 1 if c < idx else idx + 1
                new_r = r

            out[new_r][new_c] = colour

    return out