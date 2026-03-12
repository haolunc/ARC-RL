def transform(grid):

    src = [
        [(0, 0), (1, 1), (0, 4)],   
        [(3, 1), (2, 2), (1, 3)],   
        [(4, 0), (3, 3), (4, 4)]    
    ]

    out = []
    for row_map in src:
        out.append([grid[r][c] for r, c in row_map])
    return out