def transform(grid):

    n = len(grid)
    m = len(grid[0]) if n else 0

    best = None          
    best_area = 0

    for top in range(n):
        for left in range(m):
            colour = grid[top][left]
            if colour == 0:
                continue          
            for bottom in range(top, n):
                for right in range(left, m):
                    area = (bottom - top + 1) * (right - left + 1)
                    if area <= best_area:
                        continue   

                    ok = True
                    for i in range(top, bottom + 1):
                        for j in range(left, right + 1):
                            if grid[i][j] != colour:
                                ok = False
                                break
                        if not ok:
                            break

                    if ok:
                        best = (top, left, bottom, right, colour)
                        best_area = area

    out = [[0] * m for _ in range(n)]
    if best is not None:
        top, left, bottom, right, colour = best
        for i in range(top, bottom + 1):
            for j in range(left, right + 1):
                out[i][j] = colour

    return out