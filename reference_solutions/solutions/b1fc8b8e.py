def transform(grid):

    pattern = [row[2:4] for row in grid[:2]]   

    out = [[0] * 5 for _ in range(5)]

    def paste(r, c):
        for i in range(2):
            for j in range(2):
                out[r + i][c + j] = pattern[i][j]

    paste(0, 0)   
    paste(0, 3)   
    paste(3, 0)   
    paste(3, 3)   

    return out