def transform(grid):

    h = len(grid)
    w = len(grid[0])

    row4 = next(i for i in range(h) if all(cell == 4 for cell in grid[i]))
    col4 = next(j for j in range(w) if all(grid[i][j] == 4 for i in range(h)))

    out_h = row4          
    out_w = col4          

    out = [[0] * out_w for _ in range(out_h)]

    for r in range(out_h):
        for c in range(out_w):
            tl = grid[r][c]
            tr = grid[r][col4 + 1 + c]
            bl = grid[row4 + 1 + r][c]
            br = grid[row4 + 1 + r][col4 + 1 + c]

            for v in (br, tl, tr, bl):
                if v != 0:
                    out[r][c] = v
                    break

    return out