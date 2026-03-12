def transform(grid):

    rows = len(grid)
    cols = len(grid[0])

    for i in range(rows - 2):
        for j in range(cols - 2):

            win = [grid[i + r][j:j + 3] for r in range(3)]

            centre = win[1][1]
            if centre == 0:
                continue

            other = {}
            for r in range(3):
                for c in range(3):
                    if r == 1 and c == 1:   
                        continue
                    v = win[r][c]
                    if v != 0:
                        other[v] = other.get(v, 0) + 1

            if len(other) == 1:
                other_colour = next(iter(other))
                if other_colour != centre:

                    out = [row[:] for row in win]
                    out[1][1] = other_colour
                    return out

    return []