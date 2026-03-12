def transform(grid):

    if not grid:
        return grid

    rows = len(grid)
    cols = len(grid[0])

    col_counts = [0] * cols
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 5:
                col_counts[c] += 1

    max_count = -1
    max_col = None
    for c, cnt in enumerate(col_counts):
        if cnt > max_count:
            max_count = cnt
            max_col = c

    min_count = float('inf')
    min_col = None
    for c, cnt in enumerate(col_counts):
        if cnt > 0 and c != max_col and cnt < min_count:
            min_count = cnt
            min_col = c

    new_grid = []
    for r in range(rows):
        new_row = []
        for c in range(cols):
            val = grid[r][c]
            if val == 5:
                if c == max_col:
                    new_row.append(1)          
                elif c == min_col:
                    new_row.append(2)          
                else:
                    new_row.append(0)          
            else:
                new_row.append(val)            
        new_grid.append(new_row)

    return new_grid