def transform(grid):

    n = len(grid)
    m = len(grid[0])

    colour = None

    cells = []
    for i in range(n):
        for j in range(m):
            v = grid[i][j]
            if v != 0:
                colour = v
                cells.append((i, j))
    if colour is None:

        return [row[:] for row in grid]

    rows = [i for i, _ in cells]
    cols = [j for _, j in cells]
    top, bottom = min(rows), max(rows)
    left, right = min(cols), max(cols)

    if colour == 6:          
        new_top = 0
        new_left = left
    elif colour == 4:        
        new_top = n - 3
        new_left = left
    elif colour == 8:        
        new_top = top
        new_left = m - 3
    elif colour == 3:        
        new_top = top
        new_left = 0
    else:

        new_top, new_left = top, left

    out = [[0 for _ in range(m)] for _ in range(n)]

    for di in range(3):
        for dj in range(3):

            oi = top + di
            oj = left + dj
            val = grid[oi][oj]

            ni = new_top + di
            nj = new_left + dj
            out[ni][nj] = val

    return out