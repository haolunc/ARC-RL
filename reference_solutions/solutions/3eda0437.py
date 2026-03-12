def transform(grid):

    if not grid:
        return grid

    R = len(grid)          
    C = len(grid[0])       

    def is_all_zero(r1, r2, c1, c2):
        for r in range(r1, r2 + 1):
            row = grid[r]
            for c in range(c1, c2 + 1):
                if row[c] != 0:
                    return False
        return True

    best = None            

    for r1 in range(R):
        for r2 in range(r1 + 1, R):          
            for c1 in range(C):
                for c2 in range(c1, C):

                    area = (r2 - r1 + 1) * (c2 - c1 + 1)
                    if best is not None and area <= best[0]:
                        continue
                    if is_all_zero(r1, r2, c1, c2):
                        best = (area, r1, r2, c1, c2)

    if best is not None:
        _, r1, r2, c1, c2 = best
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                grid[r][c] = 6

    return grid