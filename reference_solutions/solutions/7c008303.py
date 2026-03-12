def transform(grid):

    n = 9  

    row8 = next(r for r in range(n) if all(v == 8 for v in grid[r]))
    col8 = next(c for c in range(n) if all(grid[r][c] == 8 for r in range(n)))

    top_h = row8
    bottom_h = n - row8 - 1
    left_w = col8
    right_w = n - col8 - 1

    if top_h == 6 and left_w == 6:          
        big_r, big_c = 0, 0
        small_r, small_c = row8 + 1, col8 + 1
    elif top_h == 6 and right_w == 6:       
        big_r, big_c = 0, col8 + 1
        small_r, small_c = row8 + 1, 0
    elif bottom_h == 6 and left_w == 6:     
        big_r, big_c = row8 + 1, 0
        small_r, small_c = 0, col8 + 1
    else:                                   
        big_r, big_c = row8 + 1, col8 + 1
        small_r, small_c = 0, 0

    src = [[grid[big_r + i][big_c + j] for j in range(6)] for i in range(6)]
    pat = [[grid[small_r + i][small_c + j] for j in range(2)] for i in range(2)]

    result = [[0] * 6 for _ in range(6)]
    for i in range(6):
        for j in range(6):
            if src[i][j] == 0:          
                result[i][j] = 0
            else:                       
                block_i = i // 3        
                block_j = j // 3
                result[i][j] = pat[block_i][block_j]

    return result