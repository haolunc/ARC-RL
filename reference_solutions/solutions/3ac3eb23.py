def transform(grid):

    H = len(grid)            
    W = len(grid[0]) if H else 0

    out = [[0 for _ in range(W)] for _ in range(H)]

    for r0, row in enumerate(grid):
        for c0, val in enumerate(row):
            if val == 0:
                continue
            parity = (r0 + c0) % 2

            for r in range(H):
                for dc in (-1, 0, 1):
                    c = c0 + dc
                    if 0 <= c < W and (r + c) % 2 == parity:
                        out[r][c] = val
    return out