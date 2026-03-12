def transform(grid):

    block0 = grid[0:3]
    block1 = grid[3:6]
    block2 = grid[6:9]
    block3 = grid[9:12]

    result = []
    for i in range(3):          
        row = []
        for j in range(len(grid[0])):   

            candidates = (block0[i][j], block1[i][j],
                          block3[i][j], block2[i][j])
            for val in candidates:
                if val != 0:
                    row.append(val)
                    break
            else:
                row.append(0)
        result.append(row)
    return result