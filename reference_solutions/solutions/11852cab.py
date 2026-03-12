def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    min_r, max_r = h, -1
    min_c, max_c = w, -1
    for r in range(h):
        for c in range(w):
            if grid[r][c] != 0:
                if r < min_r: min_r = r
                if r > max_r: max_r = r
                if c < min_c: min_c = c
                if c > max_c: max_c = c

    if max_r == -1:
        return [row[:] for row in grid]

    centre_r = (min_r + max_r) // 2
    centre_c = (min_c + max_c) // 2

    out = [row[:] for row in grid]   

    rotations = [lambda dr, dc: (-dc, dr),          
                 lambda dr, dc: (-dr, -dc),        
                 lambda dr, dc: (dc, -dr)]        

    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v == 0:
                continue
            dr = r - centre_r
            dc = c - centre_c
            for rot in rotations:
                dr2, dc2 = rot(dr, dc)
                nr = centre_r + dr2
                nc = centre_c + dc2
                if 0 <= nr < h and 0 <= nc < w and out[nr][nc] == 0:
                    out[nr][nc] = v

    return out