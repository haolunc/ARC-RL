def transform(grid):

    def rot90(m):

        return [list(row) for row in zip(*m[::-1])]

    def rotK(m, k):
        r = m
        for _ in range(k % 4):
            r = rot90(r)
        return r

    out_size = 12
    tile = grid  
    block = 3
    out = [[0 for _ in range(out_size)] for _ in range(out_size)]

    for bi in range(4):  
        for bj in range(4):  

            if bi in (0, 1) and bj in (0, 1):
                rot = 2  
            elif bi in (0, 1) and bj in (2, 3):
                rot = 1  
            elif bi in (2, 3) and bj in (0, 1):
                rot = 3  
            else:
                rot = 0  

            block_tile = rotK(grid, rot)

            for i in range(3):
                for j in range(3):
                    out[bi*3 + i][bj*3 + j] = block_tile[i][j]

    return out