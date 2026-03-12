def transform(grid):

    R = len(grid)
    C = len(grid[0]) if R else 0

    out = [row[:] for row in grid]

    def all_equal(seq):
        return all(x == seq[0] for x in seq)

    vertical = all_equal(grid[0]) and all_equal(grid[-1])
    if vertical:
        colour_top = grid[0][0]
        colour_bottom = grid[-1][0]
    else:

        colour_left = grid[0][0]
        colour_right = grid[0][-1]

    for r in range(R):
        for c in range(C):
            if grid[r][c] != 1:
                continue

            if vertical:
                d_top = r
                d_bottom = R - 1 - r
                if d_top < d_bottom:          
                    nr, nc = r - 1, c
                    colour = colour_top
                else:                         
                    nr, nc = r + 1, c
                    colour = colour_bottom
            else:  
                d_left = c
                d_right = C - 1 - c
                if d_left < d_right:          
                    nr, nc = r, c - 1
                    colour = colour_left
                else:                         
                    nr, nc = r, c + 1
                    colour = colour_right

            if 0 <= nr < R and 0 <= nc < C and out[nr][nc] == 0:
                out[nr][nc] = colour

    return out