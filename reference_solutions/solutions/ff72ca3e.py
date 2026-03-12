def transform(grid):

    if not grid:
        return grid

    R = len(grid)
    C = len(grid[0]) if grid else 0

    out = [row[:] for row in grid]

    fives = [(r, c) for r in range(R) for c in range(C) if grid[r][c] == 5]

    if not fives:
        return out

    for r in range(R):
        for c in range(C):
            if grid[r][c] == 4:

                d = min(max(abs(r - rf), abs(c - cf)) for (rf, cf) in fives)
                half = max(d - 1, 0)  
                r_start, r_end = r - half, r + half
                c_start, c_end = c - half, c + half

                for rr in range(r_start, r_end + 1):
                    for cc in range(c_start, c_end + 1):
                        if 0 <= rr < R and 0 <= cc < C:
                            if out[rr][cc] == 0:
                                out[rr][cc] = 2
    return out