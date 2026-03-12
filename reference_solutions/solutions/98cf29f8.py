def transform(grid):

    import copy

    rows, cols = len(grid), len(grid[0])

    def max_filled_rectangle(col):
        best = (0, 0, 0, 0, 0)          
        for r1 in range(rows):
            for r2 in range(r1, rows):
                for c1 in range(cols):
                    for c2 in range(c1, cols):
                        area = (r2 - r1 + 1) * (c2 - c1 + 1)
                        if area <= best[0]:
                            continue
                        ok = True
                        for i in range(r1, r2 + 1):
                            for j in range(c1, c2 + 1):
                                if grid[i][j] != col:
                                    ok = False
                                    break
                            if not ok:
                                break
                        if ok:
                            best = (area, r1, r2, c1, c2)
        _, r1, r2, c1, c2 = best
        return r1, r2, c1, c2

    colours = {}
    for i in range(rows):
        for j in range(cols):
            v = grid[i][j]
            if v == 0:
                continue
            colours.setdefault(v, []).append((i, j))

    rects = []          
    for col, cells in colours.items():

        r1, r2, c1, c2 = max_filled_rectangle(col)

        cr = sum(i for i, _ in cells) / len(cells)
        cc = sum(j for _, j in cells) / len(cells)

        rects.append((col, r1, r2, c1, c2, cr, cc))

    rects.sort(key=lambda x: x[0])   

    placed = []   
    for idx, (col, r1, r2, c1, c2, cr, cc) in enumerate(rects):
        if idx == 0:

            placed.append((col, r1, r2, c1, c2))
            continue

        _, pr1, pr2, pc1, pc2 = placed[-1]

        _, _, _, _, _, prc, pcc = rects[idx - 1]
        dy = cr - prc
        dx = cc - pcc

        height = r2 - r1 + 1
        width  = c2 - c1 + 1

        if abs(dx) > abs(dy):               
            if dx > 0:                      
                new_c1 = pc2 + 1
            else:                           
                new_c1 = pc1 - width
            new_r1 = r1                       
        else:                               
            if dy > 0:                      
                new_r1 = pr2 + 1
            else:                           
                new_r1 = pr1 - height
            new_c1 = c1                       

        new_r1 = max(0, min(new_r1, rows - height))
        new_c1 = max(0, min(new_c1, cols - width))

        placed.append((col,
                       new_r1,
                       new_r1 + height - 1,
                       new_c1,
                       new_c1 + width - 1))

    out = [[0 for _ in range(cols)] for _ in range(rows)]
    for col, r1, r2, c1, c2 in placed:
        for i in range(r1, r2 + 1):
            for j in range(c1, c2 + 1):
                out[i][j] = col
    return out