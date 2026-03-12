def transform(grid):

    def rotateCW(mat):
        n = len(mat)
        return [[mat[n - 1 - j][i] for j in range(n)] for i in range(n)]

    rot0 = grid
    rot90 = rotateCW(rot0)
    rot180 = rotateCW(rot90)
    rot270 = rotateCW(rot180)

    res = [[0]*6 for _ in range(6)]
    for i in range(3):
        for j in range(3):
            res[i][j] = rot0[i][j]        
            res[i][j+3] = rot270[i][j]     
            res[i+3][j] = rot180[i][j]     
            res[i+3][j+3] = rot90[i][j]     
    return res