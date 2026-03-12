def transform(grid):

    O = [row[:] for row in grid]          

    H = [row[::-1] for row in O]

    V = O[::-1]

    R = [row[::-1] for row in V]

    out = [[0] * 9 for _ in range(9)]

    for br in range(3):          
        for bc in range(3):      

            if br == 1 and bc == 1:          
                block = O
            elif br == 1:                    
                block = H
            elif bc == 1:                    
                block = V
            else:                            
                block = R

            for i in range(3):
                out_row = br * 3 + i
                out[out_row][bc * 3: bc * 3 + 3] = block[i][:]

    return out