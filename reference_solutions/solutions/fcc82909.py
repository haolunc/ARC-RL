def transform(grid):
    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    out = [row[:] for row in grid]

    for r in range(rows - 1):
        for c in range(cols - 1):

            if (grid[r][c] != 0 and grid[r][c + 1] != 0 and
                grid[r + 1][c] != 0 and grid[r + 1][c + 1] != 0):

                distinct_colors = len({
                    grid[r][c], grid[r][c + 1],
                    grid[r + 1][c], grid[r + 1][c + 1]
                })
                height = distinct_colors

                top_row = r + 2
                bottom_row = r + 1 + height  
                for i in range(top_row, bottom_row + 1):
                    if i >= rows:
                        break
                    for j in range(c, c + 2):
                        if 0 <= j < cols and out[i][j] == 0:
                            out[i][j] = 3
    return out