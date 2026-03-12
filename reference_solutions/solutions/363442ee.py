def transform(grid):

    rows = len(grid)
    cols = len(grid[0])

    out = [row[:] for row in grid]

    pattern = [[grid[r][c] for c in range(3)] for r in range(3)]

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                top = r - 1          
                left = c - 1         
                for dr in range(3):
                    for dc in range(3):
                        rr = top + dr
                        cc = left + dc
                        if 0 <= rr < rows and 0 <= cc < cols:
                            out[rr][cc] = pattern[dr][dc]

    return out