def transform(grid):

    grid = [list(row) for row in grid]
    H = len(grid)
    W = len(grid[0])

    rows = [i for i in range(H) if any(grid[i][j] != 0 for j in range(W))]
    cols = [j for j in range(W) if any(grid[i][j] != 0 for i in range(H))]

    top, bottom = min(rows), max(rows)
    left, right = min(cols), max(cols)

    pattern = [row[left:right + 1] for row in grid[top:bottom + 1]]
    ph = len(pattern)          
    pw = len(pattern[0])       

    offsets = [(i, j) for i in range(ph) for j in range(pw) if pattern[i][j] != 0]

    out = [[0] * W for _ in range(H)]

    for dr, dc in offsets:
        r0 = dr * ph
        c0 = dc * pw
        for i in range(ph):
            for j in range(pw):
                out[r0 + i][c0 + j] = pattern[i][j]

    return out