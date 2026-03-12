def transform(grid):

    H = len(grid)
    W = len(grid[0])

    boxes = {}
    for r in range(H):
        for c in range(W):
            col = grid[r][c]
            if col not in boxes:
                boxes[col] = [r, r, c, c]          
            else:
                b = boxes[col]
                b[0] = min(b[0], r)
                b[1] = max(b[1], r)
                b[2] = min(b[2], c)
                b[3] = max(b[3], c)

    def is_perimeter(col, r0, r1, c0, c1):

        for c in range(c0, c1 + 1):
            if grid[r0][c] != col or grid[r1][c] != col:
                return False

        for r in range(r0 + 1, r1):
            if grid[r][c0] != col or grid[r][c1] != col:
                return False
        return True

    frame = None
    best_area = -1
    for col, (r0, r1, c0, c1) in boxes.items():
        if is_perimeter(col, r0, r1, c0, c1):
            area = (r1 - r0 + 1) * (c1 - c0 + 1)
            if area > best_area:
                best_area = area
                frame = (col, r0, r1, c0, c1)

    if frame is None:
        raise ValueError("No frame found")

    frame_col, r0, r1, c0, c1 = frame

    inner_rows = range(r0 + 1, r1)
    inner_cols = range(c0 + 1, c1)

    inner_h = len(inner_rows)
    inner_w = len(inner_cols)

    out_size = inner_h + 2
    output = [[frame_col] * out_size for _ in range(out_size)]

    for i, ri in enumerate(inner_rows):
        for j, cj in enumerate(inner_cols):
            output[i + 1][j + 1] = grid[ri][cj]

    return output