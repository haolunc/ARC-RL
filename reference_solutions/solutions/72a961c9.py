def transform(grid):

    out = [row[:] for row in grid]

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    non_zero_counts = [sum(1 for v in row if v != 0) for row in grid]
    special_row = max(range(rows), key=lambda i: non_zero_counts[i])

    offset = {2: 4, 8: 3}

    for c in range(cols):
        colour = grid[special_row][c]
        if colour != 0 and colour != 1:          
            d = offset.get(colour, 0)              
            start = special_row - d
            if start < 0:
                start = 0
            out[start][c] = colour                

            for r in range(start + 1, special_row):
                out[r][c] = 1

    return out