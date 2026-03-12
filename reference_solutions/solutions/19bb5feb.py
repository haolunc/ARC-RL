def transform(grid):

    R = len(grid)
    C = len(grid[0]) if R else 0

    rows8 = []
    cols8 = []
    for i in range(R):
        for j in range(C):
            if grid[i][j] == 8:
                rows8.append(i)
                cols8.append(j)

    if not rows8:            
        return [[0, 0], [0, 0]]

    r_min = min(rows8)
    r_max = max(rows8)
    c_min = min(cols8)
    c_max = max(cols8)

    r_mid = (r_min + r_max) // 2
    c_mid = (c_min + c_max) // 2

    def dominant_colour(r0, r1, c0, c1):
        counter = {}
        for i in range(r0, r1 + 1):
            for j in range(c0, c1 + 1):
                v = grid[i][j]
                if v != 0 and v != 8:
                    counter[v] = counter.get(v, 0) + 1
        if not counter:
            return 0

        return max(counter, key=counter.get)

    tl = dominant_colour(r_min, r_mid, c_min, c_mid)          
    tr = dominant_colour(r_min, r_mid, c_mid + 1, c_max)      
    bl = dominant_colour(r_mid + 1, r_max, c_min, c_mid)      
    br = dominant_colour(r_mid + 1, r_max, c_mid + 1, c_max)  

    return [[tl, tr],
            [bl, br]]