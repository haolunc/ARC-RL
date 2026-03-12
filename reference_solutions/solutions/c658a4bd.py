def transform(grid):

    colour_boxes = {}   
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == 0:
                continue
            if val not in colour_boxes:
                colour_boxes[val] = [r, r, c, c]
            else:
                b = colour_boxes[val]
                b[0] = min(b[0], r)   
                b[1] = max(b[1], r)   
                b[2] = min(b[2], c)   
                b[3] = max(b[3], c)   

    colour_areas = []
    for col, (r0, r1, c0, c1) in colour_boxes.items():
        area = (r1 - r0 + 1) * (c1 - c0 + 1)
        colour_areas.append((area, col))
    colour_areas.sort()          

    _, first_col = colour_areas[0]
    r0, r1, c0, c1 = colour_boxes[first_col]
    h = r1 - r0 + 1
    w = c1 - c0 + 1
    size = max(h, w)                 
    cur = [[first_col] * size for _ in range(size)]

    for _, col in colour_areas[1:]:
        new_h = len(cur) + 2
        new_w = len(cur[0]) + 2
        new_grid = [[col] * new_w for _ in range(new_h)]
        for i in range(len(cur)):
            new_grid[i + 1][1:1 + len(cur[0])] = cur[i]
        cur = new_grid

    return cur