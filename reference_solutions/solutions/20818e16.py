def transform(grid):

    import collections

    h = len(grid)
    w = len(grid[0])

    freq = collections.Counter()
    for row in grid:
        freq.update(row)

    background = max(freq.items(), key=lambda kv: kv[1])[0]

    rects = {}          
    for r in range(h):
        for c in range(w):
            col = grid[r][c]
            if col == background:
                continue
            if col not in rects:
                rects[col] = [r, r, c, c]   
            else:
                rects[col][0] = min(rects[col][0], r)
                rects[col][1] = max(rects[col][1], r)
                rects[col][2] = min(rects[col][2], c)
                rects[col][3] = max(rects[col][3], c)

    rect_info = {}
    for col, (min_r, max_r, min_c, max_c) in rects.items():
        height = max_r - min_r + 1
        width  = max_c - min_c + 1
        area   = height * width
        rect_info[col] = (height, width, area, min_r, max_r, min_c, max_c)

    base_col, (base_h, base_w, base_area, _, _, _, _) = max(rect_info.items(),
                                                       key=lambda kv: kv[1][2])

    canvas = [[base_col for _ in range(base_w)] for _ in range(base_h)]

    others = [(col, info) for col, info in rect_info.items() if col != base_col]
    others.sort(key=lambda kv: kv[1][2], reverse=True)   

    for col, (rect_h, rect_w, _, _, _, _, _) in others:
        for i in range(rect_h):
            for j in range(rect_w):
                canvas[i][j] = col

    return canvas