def transform(grid):

    h = len(grid)
    w = len(grid[0])

    red_r = red_c = None
    for i in range(h):
        for j in range(w):
            if grid[i][j] == 2:
                red_r, red_c = i, j
                break
        if red_r is not None:
            break

    res = [row[:] for row in grid]

    left = right = red_c
    cur_r = red_r

    while cur_r > 0:
        nxt_r = cur_r - 1

        if left == right:          
            left_next = left
            right_next = left + 1
        else:                     
            left_next = left + 1
            right_next = right + 1

        while left_next < w:
            conflict = False
            if grid[nxt_r][left_next] == 1:
                conflict = True
            if right_next < w and grid[nxt_r][right_next] == 1:
                conflict = True
            if conflict:
                left_next += 1
                right_next += 1
                continue
            break

        if left_next >= w:
            break

        for c in range(left + 1, left_next + 1):
            if res[cur_r][c] != 1:          
                res[cur_r][c] = 2

        if res[nxt_r][left_next] != 1:
            res[nxt_r][left_next] = 2
        if right_next < w and res[nxt_r][right_next] != 1:
            res[nxt_r][right_next] = 2

        left, right = left_next, right_next
        cur_r = nxt_r

    return res