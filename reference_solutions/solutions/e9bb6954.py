def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    assignments = {}

    for i in range(h - 2):
        for j in range(w - 2):
            colour = grid[i][j]
            if colour == 0:
                continue
            solid = True
            for di in range(3):
                for dj in range(3):
                    if grid[i + di][j + dj] != colour:
                        solid = False
                        break
                if not solid:
                    break
            if not solid:
                continue

            rc = i + 1          
            cc = j + 1          

            for c in range(w):
                assignments.setdefault((rc, c), set()).add(colour)

            for r in range(h):
                assignments.setdefault((r, cc), set()).add(colour)

    result = [row[:] for row in grid]   
    for (r, c), colour_set in assignments.items():
        if len(colour_set) == 1:
            result[r][c] = next(iter(colour_set))
        else:          
            result[r][c] = 0

    return result