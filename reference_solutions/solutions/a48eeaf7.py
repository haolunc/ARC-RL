def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    out = [row[:] for row in grid]

    reds = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 2]
    yellows = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 5]

    def sgn(x):
        return (x > 0) - (x < 0)

    for yr, yc in yellows:

        best = None
        best_dist = None
        for rr, rc in reds:
            d = abs(rr - yr) + abs(rc - yc)
            if best_dist is None or d < best_dist:
                best_dist = d
                best = (rr, rc)

        dr = sgn(best[0] - yr)
        dc = sgn(best[1] - yc)

        cur_r, cur_c = yr, yc
        while True:
            nxt_r = cur_r + dr
            nxt_c = cur_c + dc

            if not (0 <= nxt_r < rows and 0 <= nxt_c < cols):
                break
            if grid[nxt_r][nxt_c] == 2:   
                break

            cur_r, cur_c = nxt_r, nxt_c

        out[yr][yc] = 0
        out[cur_r][cur_c] = 5

    return out