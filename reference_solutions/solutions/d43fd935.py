def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    new_grid = [row[:] for row in grid]

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            if val == 0 or val == 3:
                continue          

            for dr, dc in dirs:
                walk = []
                rr, cc = r + dr, c + dc
                while 0 <= rr < rows and 0 <= cc < cols:
                    cell = grid[rr][cc]
                    if cell != 0:               
                        if cell == 3:           
                            for pr, pc in walk:
                                new_grid[pr][pc] = val
                        break                  
                    else:
                        walk.append((rr, cc))
                    rr += dr
                    cc += dc

    return new_grid