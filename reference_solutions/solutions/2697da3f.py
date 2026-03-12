def transform(grid):

    rows = len(grid)
    cols = len(grid[0])
    min_r, max_r = rows, -1
    min_c, max_c = cols, -1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                if r < min_r: min_r = r
                if r > max_r: max_r = r
                if c < min_c: min_c = c
                if c > max_c: max_c = c

    P = [row[min_c:max_c+1] for row in grid[min_r:max_r+1]]
    h = len(P)
    w = len(P[0])

    def rotate_cw(mat):
        h0, w0 = len(mat), len(mat[0])
        return [[mat[h0-1-j][i] for j in range(h0)] for i in range(w0)]

    def rotate_ccw(mat):

        return rotate_cw(rotate_cw(rotate_cw(mat)))

    def mirror_h(mat):
        return [list(reversed(row)) for row in mat]

    N = 2 * w + h
    out = [[0] * N for _ in range(N)]

    for i in range(h):
        for j in range(w):
            out[w + i][j] = P[i][j]

    P_mirror = mirror_h(P)
    for i in range(h):
        for j in range(w):
            out[w + i][w + h + j] = P_mirror[i][j]

    P_north = rotate_cw(P)          
    for i in range(w):
        for j in range(h):
            out[i][w + j] = P_north[i][j]

    P_south = rotate_ccw(P)         
    for i in range(w):
        for j in range(h):
            out[w + h + i][w + j] = P_south[i][j]

    return out