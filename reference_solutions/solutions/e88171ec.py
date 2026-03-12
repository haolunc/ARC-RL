def transform(grid):

    h = len(grid)
    w = len(grid[0])

    zero = [[1 if grid[i][j] == 0 else 0 for j in range(w)] for i in range(h)]

    pref = [[0] * (w + 1) for _ in range(h + 1)]
    for i in range(h):
        row_sum = 0
        for j in range(w):
            row_sum += zero[i][j]
            pref[i + 1][j + 1] = pref[i][j + 1] + row_sum

    def rect_sum(r1, c1, r2, c2):

        return (pref[r2 + 1][c2 + 1] - pref[r1][c2 + 1] -
                pref[r2 + 1][c1] + pref[r1][c1])

    best = (-1, None)  

    for top in range(h):
        for bottom in range(top, h):
            height = bottom - top + 1
            for left in range(w):
                for right in range(left, w):
                    width = right - left + 1
                    area = height * width

                    if area <= best[0]:
                        continue
                    if rect_sum(top, left, bottom, right) == area:
                        best = (area, (top, bottom, left, right))

    if best[1] is None:
        return grid

    top, bottom, left, right = best[1]

    out = [row[:] for row in grid]

    for i in range(top + 1, bottom):
        for j in range(left + 1, right):
            out[i][j] = 8

    return out