def transform(grid):

    h = len(grid)
    w = len(grid[0])
    out = [[0] * w for _ in range(h)]

    for i in range(h):
        for j in range(w):
            c_center = grid[i][j]
            if c_center == 0:
                continue

            if i - 1 < 0 or i + 1 >= h or j - 1 < 0 or j + 1 >= w:
                continue

            c_arm = grid[i - 1][j]
            if c_arm == 0 or c_arm == c_center:
                continue

            if (grid[i - 1][j] == c_arm and
                grid[i + 1][j] == c_arm and
                grid[i][j - 1] == c_arm and
                grid[i][j + 1] == c_arm):

                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        y = i + dy
                        x = j + dx
                        if 0 <= y < h and 0 <= x < w:
                            if abs(dx) == abs(dy):          
                                out[y][x] = c_center
                            elif dx == 0 or dy == 0:       
                                out[y][x] = c_arm
    return out