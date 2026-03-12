def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    marked_rows = {i for i in range(h) if grid[i][0] == 4 and grid[i][-1] == 4}

    marked_cols = {j for j in range(w) if grid[0][j] == 4 and grid[-1][j] == 4}

    swap = {0: 8, 8: 0, 6: 7, 7: 6}

    out = []
    for i in range(h):
        row_out = []
        for j in range(w):
            val = grid[i][j]
            if (i in marked_rows or j in marked_cols) and val != 4:
                val = swap.get(val, val)   
            row_out.append(val)
        out.append(row_out)

    return out