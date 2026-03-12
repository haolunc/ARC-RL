def transform(grid):

    H = len(grid)
    W = len(grid[0])

    sep_rows = []
    sep_color = None
    for i, row in enumerate(grid):
        if all(v == row[0] for v in row) and row[0] != 0:
            sep_rows.append(i)
            sep_color = row[0]               
    sep_cols = []
    for j in range(W):
        col = [grid[i][j] for i in range(H)]
        if all(v == col[0] for v in col) and col[0] != 0:
            sep_cols.append(j)
            sep_color = col[0]

    block_rows = []
    prev = -1
    for r in sep_rows + [H]:
        block_rows.append((prev + 1, r - 1))
        prev = r
    block_cols = []
    prev = -1
    for c in sep_cols + [W]:
        block_cols.append((prev + 1, c - 1))
        prev = c

    template = None
    ti = tj = None
    for i, (r0, r1) in enumerate(block_rows):
        for j, (c0, c1) in enumerate(block_cols):

            found = False
            for r in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    v = grid[r][c]
                    if v != 0 and v != sep_color:
                        found = True
                        break
                if found:
                    break
            if found:

                template = [grid[r][c0:c1 + 1] for r in range(r0, r1 + 1)]
                ti, tj = i, j
                break
        if template is not None:
            break

    out = [row[:] for row in grid]          
    if template is None:                    
        return out

    for i, (r0, r1) in enumerate(block_rows):
        if (i % 2) != (ti % 2):
            continue
        for j, (c0, c1) in enumerate(block_cols):
            if (j % 2) != (tj % 2):
                continue

            for dr, r in enumerate(range(r0, r1 + 1)):
                for dc, c in enumerate(range(c0, c1 + 1)):
                    out[r][c] = template[dr][dc]

    return out