def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    row_of_2 = None
    for r in range(h):
        if all(cell == 2 for cell in grid[r]):
            row_of_2 = r
            break
    if row_of_2 is None:

        return [row[:] for row in grid]

    out = [[0 for _ in range(w)] for _ in range(h)]
    out[row_of_2] = [2] * w

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 4:
                continue

            new_r = r + 1
            if 0 <= new_r < h and out[new_r][c] != 2:
                out[new_r][c] = 4

            if r == row_of_2 - 2:

                base_r = row_of_2 - 1

                d = 1
                while base_r - d >= 0 and c - d >= 0:
                    out[base_r - d][c - d] = 4
                    d += 1

                d = 1
                while base_r - d >= 0 and c + d < w:
                    out[base_r - d][c + d] = 4
                    d += 1

    return out