def transform(grid):

    h = len(grid)
    w = len(grid[0])

    best = None  
    for pr in range(1, h + 1):
        for pc in range(1, w + 1):

            pattern = [[None for _ in range(pc)] for _ in range(pr)]
            ok = True
            for i in range(h):
                row = grid[i]
                for j in range(w):
                    val = row[j]
                    if val == 0:
                        continue
                    pi, pj = i % pr, j % pc
                    if pattern[pi][pj] is None:
                        pattern[pi][pj] = val
                    elif pattern[pi][pj] != val:
                        ok = False
                        break
                if not ok:
                    break
            if ok:

                if best is None or pr * pc < best[0] * best[1]:
                    best = (pr, pc, pattern)

    if best is None:
        return [row[:] for row in grid]

    pr, pc, pattern = best

    out = [[0] * w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            out[i][j] = pattern[i % pr][j % pc]
    return out