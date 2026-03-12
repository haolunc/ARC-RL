def transform(grid):
    import copy
    h = len(grid)
    w = len(grid[0])
    out = copy.deepcopy(grid)

    def set_cell(r, c, val):
        if 0 <= r < h and 0 <= c < w:
            out[r][c] = val

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 3:          

                for dc in range(-2, 3):
                    set_cell(r - 2, c + dc, 5)

                set_cell(r - 1, c, 5)

                for dr in (-1, 0, 1):
                    set_cell(r + dr, c - 2, 2)
                    set_cell(r + dr, c + 2, 2)

                for cc in range(w):
                    set_cell(r + 2, cc, 2)
                for dc in range(-2, 3):
                    set_cell(r + 2, c + dc, 8)

    return out