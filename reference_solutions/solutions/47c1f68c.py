def transform(grid):

    n = len(grid)
    if n == 0:
        return []

    k = n // 2                     
    C = grid[k][k]                 

    out_size = 2 * k

    out = [[0 for _ in range(out_size)] for _ in range(out_size)]

    for i in range(k):
        for j in range(k):
            if grid[i][j] != 0:   

                out[i][j] = C                                   
                out[i][out_size - 1 - j] = C                    
                out[out_size - 1 - i][j] = C                    
                out[out_size - 1 - i][out_size - 1 - j] = C     
    return out