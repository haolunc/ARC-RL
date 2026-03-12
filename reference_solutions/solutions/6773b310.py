def transform(grid):

    starts = [0, 4, 8]          
    out = []

    for r0 in starts:           
        out_row = []
        for c0 in starts:       
            cnt6 = 0
            for dr in range(3):
                for dc in range(3):
                    if grid[r0 + dr][c0 + dc] == 6:
                        cnt6 += 1
            out_row.append(1 if cnt6 == 2 else 0)
        out.append(out_row)

    return out