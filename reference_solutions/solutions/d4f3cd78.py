def transform(grid):

    g = [row[:] for row in grid]
    R, C = len(g), len(g[0])

    five_cells = [(r, c) for r in range(R) for c in range(C) if g[r][c] == 5]
    if not five_cells:
        return g  

    rows, cols = zip(*five_cells)
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)

    for r in range(min_r + 1, max_r):
        for c in range(min_c + 1, max_c):
            g[r][c] = 8

    openings = []          

    for c in range(min_c + 1, max_c):
        if g[min_r][c] != 5:
            openings.append((min_r, c, -1, 0))

    for c in range(min_c + 1, max_c):
        if g[max_r][c] != 5:
            openings.append((max_r, c, 1, 0))

    for r in range(min_r + 1, max_r):
        if g[r][min_c] != 5:
            openings.append((r, min_c, 0, -1))

    for r in range(min_r + 1, max_r):
        if g[r][max_c] != 5:
            openings.append((r, max_c, 0, 1))

    for r, c, dr, dc in openings:
        g[r][c] = 8
        nr, nc = r + dr, c + dc
        while 0 <= nr < R and 0 <= nc < C:
            g[nr][nc] = 8
            nr += dr
            nc += dc

    return g