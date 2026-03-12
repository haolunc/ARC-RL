def transform(grid):

    left = [row[1:4] for row in grid[1:4]]   
    right = [row[5:8] for row in grid[1:4]]  

    top = left[0]                     
    k = sum(1 for v in top if v == 5)  

    if k == 3:
        colour = 1
    elif k == 2:
        if top[0] == 0:   
            colour = 3
        else:             
            colour = 2
    else:
        colour = 1  

    out = []
    for i in range(3):
        out_row = []
        for j in range(3):
            out_row.append(colour if right[i][j] == 5 else 0)
        out.append(out_row)

    return out