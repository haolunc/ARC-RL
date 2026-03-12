def transform(grid):

    def bounding_box(cells):
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        return min(rows), max(rows), min(cols), max(cols)

    h = len(grid)
    w = len(grid[0]) if h else 0
    colour_cells = {}
    for i in range(h):
        for j in range(w):
            col = grid[i][j]
            if col != 0:
                colour_cells.setdefault(col, []).append((i, j))

    border_colour = None
    border_bbox = None
    for col, cells in colour_cells.items():
        top, bottom, left, right = bounding_box(cells)
        bh = bottom - top + 1
        bw = right - left + 1
        perimeter = 2 * (bh + bw) - 4
        if len(cells) == perimeter:
            border_colour = col
            border_bbox = (top, bottom, left, right)
            break

    if border_colour is None:
        raise ValueError("No border colour found")

    inner_colour = None
    for col in colour_cells:
        if col != border_colour:
            inner_colour = col
            break
    if inner_colour is None:
        raise ValueError("No inner colour found")

    inner_cells = colour_cells[inner_colour]
    itop, ibottom, ileft, iright = bounding_box(inner_cells)
    inner_h = ibottom - itop + 1
    inner_w = iright - ileft + 1

    P = [[0] * inner_w for _ in range(inner_h)]
    for i, j in inner_cells:
        P[i - itop][j - ileft] = inner_colour

    btop, bbottom, bleft, bright = border_bbox
    interior_h = (bbottom - btop + 1) - 2
    interior_w = (bright - bleft + 1) - 2
    k = min(interior_h, interior_w) // inner_h
    if k == 0:
        k = 1  
    out_side = 2 + k * inner_h   

    O = [[0] * out_side for _ in range(out_side)]

    for i in range(out_side):
        O[0][i] = border_colour
        O[-1][i] = border_colour
        O[i][0] = border_colour
        O[i][-1] = border_colour

    for i in range(inner_h):
        for j in range(inner_w):
            val = P[i][j]
            if val == 0:
                continue
            for di in range(k):
                for dj in range(k):
                    O[1 + i * k + di][1 + j * k + dj] = val

    return O