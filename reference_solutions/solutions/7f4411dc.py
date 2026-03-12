def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    out = [[0 for _ in range(w)] for _ in range(h)]

    colours = {grid[i][j] for i in range(h) for j in range(w) if grid[i][j] != 0}

    for col in colours:

        for r1 in range(h - 1):
            for c1 in range(w - 1):
                for r2 in range(r1 + 1, h):
                    for c2 in range(c1 + 1, w):

                        if (grid[r1][c1] != col or grid[r1][c2] != col or
                            grid[r2][c1] != col or grid[r2][c2] != col):
                            continue

                        ok = True
                        for i in range(r1, r2 + 1):
                            for j in range(c1, c2 + 1):
                                if grid[i][j] != col:
                                    ok = False
                                    break
                            if not ok:
                                break

                        if ok:

                            for i in range(r1, r2 + 1):
                                for j in range(c1, c2 + 1):
                                    out[i][j] = col

    return out