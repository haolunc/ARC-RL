def transform(grid):

    from collections import Counter

    h = len(grid)
    w = len(grid[0])

    zero_rows = [r for r in range(h) if all(cell == 0 for cell in grid[r])]
    zero_cols = [c for c in range(w) if all(grid[r][0] == 0 for r in range(h))]  

    zero_cols = [c for c in range(w) if all(grid[r][c] == 0 for r in range(h))]

    row_groups = len(zero_rows) - 1          
    col_groups = len(zero_cols) - 1          

    out_rows = row_groups + 2                
    out_cols = col_groups + 2                
    output = [[0 for _ in range(out_cols)] for _ in range(out_rows)]

    for i in range(row_groups):

        r_start = zero_rows[i] + 1
        r_end   = zero_rows[i + 1] - 1

        for j in range(col_groups):

            c_start = zero_cols[j] + 1
            c_end   = zero_cols[j + 1] - 1

            colours = []
            for r in range(r_start, r_end + 1):
                for c in range(c_start, c_end + 1):
                    val = grid[r][c]
                    if val != 0:
                        colours.append(val)

            if colours:
                cnt = Counter(colours)
                most_common = cnt.most_common()
                max_freq = most_common[0][1]

                mode_val = min(col for col, freq in most_common if freq == max_freq)
                output[i + 1][j + 1] = mode_val
            else:
                output[i + 1][j + 1] = 0  

    return output