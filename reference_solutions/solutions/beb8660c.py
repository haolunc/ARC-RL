def transform(grid):

    H = len(grid)
    if H == 0:
        return []
    W = len(grid[0])

    segments = []
    for row in grid:

        nonzeros = [v for v in row if v != 0]
        if nonzeros:
            colour = nonzeros[0]          
            length = len(nonzeros)
            segments.append((length, colour))

    segments.sort(key=lambda x: x[0])

    out = [[0] * W for _ in range(H)]

    K = len(segments)                     
    for i, (length, colour) in enumerate(segments):
        target_row = H - K + i            
        start_col = W - length            
        for c in range(start_col, W):
            out[target_row][c] = colour

    return out