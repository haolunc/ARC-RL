def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    out = [[0 for _ in range(cols)] for _ in range(rows)]

    diag = {
        (-1, -1): 3,   
        (-1, +1): 6,   
        (+1, -1): 8,   
        (+1, +1): 7    
    }

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:               

                for dr, dc in diag:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        out[nr][nc] = diag[(dr, dc)]
    return out