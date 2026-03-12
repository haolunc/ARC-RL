def transform(grid):

    h = len(grid)
    w = len(grid[0])

    best_len = -1
    C = None
    top = left = right = None

    for r in range(h):
        c = 0
        while c < w:
            if grid[r][c] == 0:
                c += 1
                continue
            colour = grid[r][c]
            start = c
            while c < w and grid[r][c] == colour:
                c += 1
            seg_len = c - start
            if seg_len > best_len:
                best_len = seg_len
                C = colour
                top = r
                left = start
                right = c - 1          

    bottom_exclusive = h               
    for r in range(top + 1, h):
        if grid[r][left] != C:        
            bottom_exclusive = r
            break

        full = True
        for c in range(left, right + 1):
            if grid[r][c] != C:
                full = False
                break
        if full:                       
            bottom_exclusive = r
            break

    interior = []
    for r in range(top + 1, bottom_exclusive):
        interior.append(grid[r][left + 1 : right])
    return interior