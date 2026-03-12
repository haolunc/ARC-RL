def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [[0 for _ in range(w)] for _ in range(h)]

    dirs = [(-1, -1), (1, 1),   
            (-1,  1), (1, -1)]   

    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v == 0:
                continue

            out[r][c] = v          

            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while 0 <= nr < h and 0 <= nc < w:
                    out[nr][nc] = v
                    nr += dr
                    nc += dc

    return out