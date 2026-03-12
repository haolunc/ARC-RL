def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [row[:] for row in grid]

    for c in range(w):

        two_cnt = sum(1 for r in range(h) if grid[r][c] == 2)

        for r in range(h):
            if grid[r][c] == 2:
                out[r][c] = 0

        top_one = -1
        for r in range(h):
            if grid[r][c] == 1:
                top_one = r
                break

        r = top_one + 1
        while two_cnt > 0 and r < h:
            if out[r][c] == 0:          
                out[r][c] = 2
                two_cnt -= 1
            r += 1

    return out