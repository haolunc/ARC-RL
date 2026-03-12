def transform(grid):

    h = len(grid)
    w = len(grid[0])
    centre = w // 2                     
    out_w = centre                     

    out = [row[:out_w] for row in grid]

    for i in range(h):
        for c in range(centre + 1, w):
            val = grid[i][c]
            if val != 0:
                target = w - 1 - c   
                if 0 <= target < out_w:
                    out[i][target] = val
    return out