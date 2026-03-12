def transform(grid):

    n = len(grid)                 
    mid = n // 2                  

    quadrants = [
        (0,      mid, 0,      mid),   
        (0,      mid, mid+1,  n),     
        (mid+1,  n,   0,      mid),   
        (mid+1,  n,   mid+1,  n)      
    ]

    for r0, r1, c0, c1 in quadrants:
        sub = [row[c0:c1] for row in grid[r0:r1]]

        background = sub[0][0]
        if any(cell != background for row in sub for cell in row):
            return sub

    return []