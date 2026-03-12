def transform(grid):

    if not grid:
        return []

    H = len(grid)
    W = len(grid[0])

    row_groups = [
        [0],                     
        list(range(1, H - 1)),  
        [H - 1]                  
    ]
    col_groups = [
        [0],                     
        list(range(1, W - 1)),  
        [W - 1]                  
    ]

    result = [[0 for _ in range(3)] for _ in range(3)]

    for i in range(3):
        for j in range(3):
            found = False
            for r in row_groups[i]:
                for c in col_groups[j]:
                    val = grid[r][c]
                    if val != 0:
                        result[i][j] = val
                        found = True
                        break
                if found:
                    break

    return result