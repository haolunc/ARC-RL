def transform(grid):

    orig = [row[:] for row in grid]          

    mirror = [list(reversed(row)) for row in grid]

    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    out = []  

    for block_row in range(3):          

        block = orig if block_row != 1 else mirror

        for r in range(h):

            new_row = block[r] * 3      
            out.append(new_row)

    return out