def transform(grid):

    h = len(grid)
    w = len(grid[0])

    out = [[8 for _ in range(w)] for _ in range(h)]

    shift = {
        1: (0, 1),   
        2: (0, -2),  
        7: (-2, 0),  
        9: (2, 0)    
    }

    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 8:
                dr, dc = shift.get(v, (0, 0))
                nr, nc = r + dr, c + dc

                out[nr][nc] = v

    return out