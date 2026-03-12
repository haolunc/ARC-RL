def transform(grid):

    output = []
    for row in grid:
        left = row[:3]      
        right = row[4:7]    
        output.append([3 if left[i] == right[i] else 0 for i in range(3)])
    return output