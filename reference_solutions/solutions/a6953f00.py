def transform(grid):

    h = len(grid)          
    w = len(grid[0])       

    start_col = 0 if h % 2 == 1 else w - 2

    result = [row[start_col:start_col + 2] for row in grid[:2]]
    return result