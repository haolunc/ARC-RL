def transform(grid):

    result = [row[:] for row in grid]
    h = len(grid)
    w = len(grid[0]) if h else 0

    def border_is_all_2(t, l, b, r):

        for c in range(l, r + 1):
            if grid[t][c] != 2 or grid[b][c] != 2:
                return False

        for rr in range(t + 1, b):
            if grid[rr][l] != 2 or grid[rr][r] != 2:
                return False
        return True

    def fill_interior(t, l, b, r):
        for rr in range(t + 1, b):
            for cc in range(l + 1, r):
                if result[rr][cc] != 2:
                    result[rr][cc] = 1

    for top in range(h - 2):
        for left in range(w - 2):
            for bottom in range(top + 2, h):
                for right in range(left + 2, w):
                    if border_is_all_2(top, left, bottom, right):
                        fill_interior(top, left, bottom, right)

    return result