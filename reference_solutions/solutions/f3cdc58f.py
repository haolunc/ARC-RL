def transform(grid):

    if not grid:
        return []

    H = len(grid)          
    W = len(grid[0])       

    counts = {k: 0 for k in range(1, 5)}
    for row in grid:
        for v in row:
            if 1 <= v <= 4:
                counts[v] += 1

    out = [[0] * W for _ in range(H)]

    for k in range(1, 5):
        cnt = counts[k]
        start_row = H - cnt               
        for r in range(start_row, H):
            out[r][k - 1] = k

    return out