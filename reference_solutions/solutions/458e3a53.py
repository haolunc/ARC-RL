def transform(grid):

    n = len(grid)          
    m = len(grid[0])       

    sep_rows = [i for i in range(n)
                if all(grid[i][j] == grid[i][0] for j in range(m))]

    sep_cols = [j for j in range(m)
                if all(grid[i][j] == grid[0][j] for i in range(n))]

    row_intervals = []
    prev = -1
    for r in sep_rows + [n]:
        row_intervals.append((prev + 1, r - 1))
        prev = r

    col_intervals = []
    prev = -1
    for c in sep_cols + [m]:
        col_intervals.append((prev + 1, c - 1))
        prev = c

    uniform = []                       
    for r0, r1 in row_intervals:
        line = []
        for c0, c1 in col_intervals:
            if r0 > r1 or c0 > c1:    
                line.append(None)
                continue
            first = grid[r0][c0]
            uniform_block = True
            for i in range(r0, r1 + 1):
                for j in range(c0, c1 + 1):
                    if grid[i][j] != first:
                        uniform_block = False
                        break
                if not uniform_block:
                    break
            line.append(first if uniform_block else None)
        uniform.append(line)

    rows_keep = [i for i, row in enumerate(uniform)
                if any(v is not None for v in row)]
    if not rows_keep:               
        return []

    cols_keep = [j for j in range(len(uniform[0]))
                if any(uniform[i][j] is not None for i in rows_keep)]

    result = [[uniform[i][j] for j in cols_keep] for i in rows_keep]
    return result