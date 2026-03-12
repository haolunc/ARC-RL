def transform(grid):

    h = len(grid)
    w = len(grid[0])

    out = [row[:] for row in grid]

    for i in range(h - 2):
        for j in range(w - 2):

            outer_coords = [
                (i, j), (i, j + 1), (i, j + 2),
                (i + 1, j + 2),
                (i + 2, j + 2), (i + 2, j + 1), (i + 2, j),
                (i + 1, j)
            ]

            if all(grid[x][y] != 7 for (x, y) in outer_coords):

                tl = grid[i][j]
                tr = grid[i][j + 2]
                br = grid[i + 2][j + 2]
                bl = grid[i + 2][j]

                top = grid[i][j + 1]
                right = grid[i + 1][j + 2]
                bottom = grid[i + 2][j + 1]
                left = grid[i + 1][j]

                out[i][j] = tr          
                out[i][j + 2] = br      
                out[i + 2][j + 2] = bl  
                out[i + 2][j] = tl      

                out[i][j + 1] = left        
                out[i + 1][j + 2] = top     
                out[i + 2][j + 1] = right   
                out[i + 1][j] = bottom      

    return out