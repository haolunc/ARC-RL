def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    rows8 = [r for r in range(h) if any(cell == 8 for cell in grid[r])]
    cols8 = [c for c in range(w) if any(grid[r][c] == 8 for r in range(h))]
    if not rows8 or not cols8:          
        return []

    rmin, rmax = min(rows8), max(rows8)
    cmin, cmax = min(cols8), max(cols8)

    pattern = [grid[r][cmin:cmax+1] for r in range(rmin, rmax+1)]

    cnt4 = sum(cell == 4 for row in grid for cell in row)

    repeated = [row * cnt4 for row in pattern]   

    while len(repeated) < 3:
        repeated.insert(0, [0] * len(repeated[0]))

    return repeated