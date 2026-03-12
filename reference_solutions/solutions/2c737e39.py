def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    fives = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == 5]

    def is_cluster_five(r, c):
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < h and 0 <= nc < w:
                val = grid[nr][nc]
                if val != 0 and val != 5:
                    return True
        return False

    source5 = target5 = None
    for r, c in fives:
        if is_cluster_five(r, c):
            source5 = (r, c)
        else:
            target5 = (r, c)

    if source5 is None or target5 is None:
        return grid

    dr = target5[0] - source5[0]
    dc = target5[1] - source5[1]

    out = [row[:] for row in grid]

    out[target5[0]][target5[1]] = 0

    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val != 0 and val != 5:          
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w:
                    out[nr][nc] = val

    return out