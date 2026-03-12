def transform(grid):

    g = [row[:] for row in grid]
    h = len(g)
    w = len(g[0]) if h else 0

    centres = []
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            if g[r][c] != 3:
                continue
            if (g[r - 1][c] == 3 and g[r + 1][c] == 3 and
                g[r][c - 1] == 3 and g[r][c + 1] == 3):
                centres.append((r, c))

    n = len(centres)
    for i in range(n):
        r1, c1 = centres[i]
        for j in range(i + 1, n):
            r2, c2 = centres[j]
            dr = r2 - r1
            dc = c2 - c1
            if abs(dr) != abs(dc):
                continue            
            step_r = 1 if dr > 0 else -1
            step_c = 1 if dc > 0 else -1
            r, c = r1 + step_r, c1 + step_c
            while (r, c) != (r2, c2):
                if g[r][c] == 0:    
                    g[r][c] = 2
                r += step_r
                c += step_c

    return g