def transform(grid):

    R = len(grid)
    C = len(grid[0]) if R else 0

    sep_rows = [r for r in range(R) if all(grid[r][c] == 5 for c in range(C))]

    sep_cols = [c for c in range(C) if all(grid[r][c] == 5 for r in range(R))]

    row_intervals = []
    start = 0
    for r in sep_rows:
        row_intervals.append((start, r - 1))
        start = r + 1
    row_intervals.append((start, R - 1))

    col_intervals = []
    start = 0
    for c in sep_cols:
        col_intervals.append((start, c - 1))
        start = c + 1
    col_intervals.append((start, C - 1))

    cells = [
        (row_intervals[0],
         col_intervals[0],
         1),                                          
        (row_intervals[len(row_intervals) // 2],
         col_intervals[len(col_intervals) // 2],
         2),                                          
        (row_intervals[-1],
         col_intervals[-1],
         3)                                           
    ]

    out = [list(row) for row in grid]   
    for (r0, r1), (c0, c1), colour in cells:
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if out[r][c] != 5:      
                    out[r][c] = colour
    return out