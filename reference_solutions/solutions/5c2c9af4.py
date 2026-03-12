def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h>0 else 0

    pts = []
    color = None
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 0:
                pts.append((r,c))
                color = v if color is None else color

    if not pts or color is None:
        return [row[:] for row in grid]

    rs = [p[0] for p in pts]
    cs = [p[1] for p in pts]
    minr, maxr = min(rs), max(rs)
    minc, maxc = min(cs), max(cs)
    center_r = (minr + maxr) // 2
    center_c = (minc + maxc) // 2

    s_r = abs(maxr - center_r)
    s_c = abs(maxc - center_c)
    s = max(s_r, s_c)

    if s == 0:
        s = None
        n = len(pts)
        for i in range(n):
            for j in range(i+1,n):
                d = max(abs(pts[i][0]-pts[j][0]), abs(pts[i][1]-pts[j][1]))
                if d>0 and (s is None or d < s):
                    s = d
        if s is None:

            return [row[:] for row in grid]

    out = [[0]*w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            d = max(abs(r - center_r), abs(c - center_c))
            if s > 0 and d % s == 0:
                out[r][c] = color
            else:
                out[r][c] = 0

    return out