def transform(grid):

    if not grid:
        return []

    H = len(grid)          
    W = len(grid[0])       

    OH = 2 * H
    OW = 2 * W

    out = [[0 for _ in range(OW)] for _ in range(OH)]

    for r in range(H):
        for c in range(W):
            v = grid[r][c]
            if v == 0:
                continue
            for dr in (0, H):
                for dc in (0, W):
                    out[r + dr][c + dc] = v

    for r in range(H):
        for c in range(W):
            v = grid[r][c]
            if v == 0:
                continue
            for dr in (0, H):
                for dc in (0, W):
                    rr = r + dr
                    cc = c + dc
                    for nr, nc in ((rr - 1, cc - 1), (rr - 1, cc + 1),
                                   (rr + 1, cc - 1), (rr + 1, cc + 1)):
                        if 0 <= nr < OH and 0 <= nc < OW and out[nr][nc] == 0:
                            out[nr][nc] = 8

    return out