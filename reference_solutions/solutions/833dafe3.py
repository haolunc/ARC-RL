def transform(grid):

    h = len(grid)
    if h == 0:
        return []
    w = len(grid[0])

    top = []
    for i in range(h - 1, -1, -1):          
        row = grid[i]
        rev = row[::-1]                    
        top.append(rev + row)              

    bottom = top[::-1]

    return top + bottom