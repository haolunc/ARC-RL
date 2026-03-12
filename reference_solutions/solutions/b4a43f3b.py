def transform(grid):

    h = len(grid)
    w = len(grid[0])

    sep = 0
    for r in range(h):
        if all(cell == 5 for cell in grid[r]):
            sep = r
            break

    N = w // 2

    pattern = [[0] * N for _ in range(N)]
    for br in range(N):
        for bc in range(N):
            r0 = br * 2
            c0 = bc * 2
            pattern[br][bc] = grid[r0][c0]

    templ = grid[sep + 1:]          
    T = len(templ)

    out_h = T * N
    out_w = w * N
    out = [[0] * out_w for _ in range(out_h)]

    for tr in range(T):
        for tc in range(w):
            if templ[tr][tc] != 0:               
                base_r = tr * N
                base_c = tc * N
                for dr in range(N):
                    for dc in range(N):
                        out[base_r + dr][base_c + dc] = pattern[dr][dc]

    return out