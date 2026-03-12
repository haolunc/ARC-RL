def transform(grid):

    h = len(grid)          
    w = len(grid[0])       

    if w == 2 * h:                     
        n = h
        left  = [row[:n] for row in grid]
        right = [row[n:] for row in grid]

        if any(8 in row for row in left):
            mask_half = left
            src_half  = right
        else:
            mask_half = right
            src_half  = left
    elif h == 2 * w:                   
        n = w
        top    = [grid[i] for i in range(n)]
        bottom = [grid[i] for i in range(n, 2 * n)]
        if any(8 in row for row in top):
            mask_half = top
            src_half  = bottom
        else:
            mask_half = bottom
            src_half  = top
    else:
        raise ValueError("Input size does not match the expected n x 2n or 2n x n pattern.")

    mask = [[1 if mask_half[i][j] == 8 else 0 for j in range(n)] for i in range(n)]

    out_size = n * n
    out = [[0 for _ in range(out_size)] for _ in range(out_size)]

    for i in range(n):
        for j in range(n):
            val = src_half[i][j]
            if val == 0:
                continue
            for di in range(n):
                for dj in range(n):
                    if mask[di][dj]:
                        out[i * n + di][j * n + dj] = val
    return out