def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    pos8 = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 8]
    if not pos8:
        return [[0] * w for _ in range(h)]  
    r0 = min(r for r, _ in pos8)
    c0 = min(c for _, c in pos8)

    others = [(r, c, grid[r][c])
              for r in range(h)
              for c in range(w)
              if grid[r][c] != 0 and grid[r][c] != 8]

    others.sort(key=lambda x: (x[0], x[1]))

    top_two = others[:2]
    bottom_two = others[2:4]

    top_two.sort(key=lambda x: x[1])
    bottom_two.sort(key=lambda x: x[1])

    out = [[0] * w for _ in range(h)]

    out[r0][c0] = top_two[0][2]          
    out[r0][c0 + 1] = top_two[1][2]      
    out[r0 + 1][c0] = bottom_two[0][2]   
    out[r0 + 1][c0 + 1] = bottom_two[1][2]  

    return out