def transform(grid):

    H = len(grid)
    W = len(grid[0])

    def find_period(length, other_len, get_val):

        for p in range(1, length + 1):
            ok = True

            known = [dict() for _ in range(p)]
            for i in range(length):
                r = i % p
                for j in range(other_len):
                    v = get_val(i, j)
                    if v == 0:
                        continue
                    if j in known[r] and known[r][j] != v:
                        ok = False
                        break
                    known[r][j] = v
                if not ok:
                    break
            if ok:
                return p
        return length  

    pR = find_period(H, W, lambda i, j: grid[i][j])

    pC = find_period(W, H, lambda j, i: grid[i][j])   

    pattern = [[0] * pC for _ in range(pR)]
    for i in range(H):
        for j in range(W):
            v = grid[i][j]
            if v != 0:
                pattern[i % pR][j % pC] = v

    out = [[0] * W for _ in range(H)]
    for i in range(H):
        for j in range(W):
            out[i][j] = pattern[i % pR][j % pC]

    return out