def transform(grid):

    N = len(grid)

    rev_col = []
    for c in range(N):
        col = [grid[r][c] for r in range(N)]
        rev_col.append(col[::-1])          

    top = []
    for i in range(N):
        top.append(grid[i] + rev_col[i])   

    bottom = [list(reversed(row)) for row in reversed(top)]

    return top + bottom