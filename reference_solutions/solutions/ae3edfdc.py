def transform(grid):

    def sign(x):
        return (x > 0) - (x < 0)

    h = len(grid)
    w = len(grid[0]) if h else 0

    from collections import Counter, defaultdict

    cnt = Counter()
    pos = defaultdict(list)          

    for r in range(h):
        row = grid[r]
        for c in range(w):
            col = row[c]
            if col != 0:
                cnt[col] += 1
                pos[col].append((r, c))

    centres = []
    for col, lst in pos.items():
        if cnt[col] == 1:
            r0, c0 = lst[0]
            centres.append((r0, c0, col))

    out = [row[:] for row in grid]
    to_erase = set()

    for rc, cc, centre_col in centres:
        for sat_col, sat_positions in pos.items():
            if sat_col == centre_col or cnt[sat_col] == 1:
                continue          
            for rs, cs in sat_positions:
                if rs == rc or cs == cc:          
                    dr = sign(rs - rc)
                    dc = sign(cs - cc)
                    tr = rc + dr
                    tc = cc + dc
                    if 0 <= tr < h and 0 <= tc < w:
                        out[tr][tc] = sat_col
                    to_erase.add((rs, cs))

    for r, c in to_erase:
        out[r][c] = 0

    return out