def transform(grid):

    R = len(grid)
    C = len(grid[0])

    colours = {grid[i][j] for i in range(R) for j in range(C) if grid[i][j] != 0}

    best = (-1, None, None, None, None, None)   
    for P in colours:
        for top in range(R - 1):
            for left in range(C - 1):
                for bottom in range(top + 1, R):
                    for right in range(left + 1, C):

                        if (grid[top][left] != P or grid[top][right] != P or
                            grid[bottom][left] != P or grid[bottom][right] != P):
                            continue
                        ok = True

                        for j in range(left, right + 1):
                            if grid[top][j] != P or grid[bottom][j] != P:
                                ok = False
                                break
                        if not ok:
                            continue

                        for i in range(top + 1, bottom):
                            if grid[i][left] != P or grid[i][right] != P:
                                ok = False
                                break
                        if not ok:
                            continue
                        area = (bottom - top + 1) * (right - left + 1)
                        if area > best[0]:
                            best = (area, top, left, bottom, right, P)

    _, top, left, bottom, right, primary = best
    H = bottom - top + 1
    W = right - left + 1

    from collections import Counter
    cnt = Counter()
    for i in range(top + 1, bottom):
        for j in range(left + 1, right):
            c = grid[i][j]
            if c != 0 and c != primary:
                cnt[c] += 1

    secondary = max(cnt.items(), key=lambda x: x[1])[0]

    out = [[0] * W for _ in range(H)]

    for j in range(W):
        out[0][j] = secondary
        out[H - 1][j] = secondary
    for i in range(H):
        out[i][0] = secondary
        out[i][W - 1] = secondary

    for i in range(1, H - 1):
        for j in range(1, W - 1):
            if grid[top + i][left + j] == secondary:
                out[i][j] = secondary

    return out