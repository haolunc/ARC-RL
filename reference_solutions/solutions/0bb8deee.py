def transform(grid):

    h, w = len(grid), len(grid[0])
    row_color = None
    for i, row in enumerate(grid):
        if all(v == row[0] and v != 0 for v in row):
            row_color = row[0]
            cross_row = i
            break

    cross_col = None
    for j in range(w):
        col = [grid[i][j] for i in range(h)]
        if all(v == row_color and v != 0 for v in col):
            cross_col = j
            break

    def quadrant(r0, r1, c0, c1):
        sub = [row[c0:c1] for row in grid[r0:r1]]

        while sub and all(v == 0 for v in sub[0]):
            sub.pop(0)
        while sub and all(v == 0 for v in sub[-1]):
            sub.pop()

        if sub:
            trans = list(zip(*sub))
            while trans and all(v == 0 for v in trans[0]):
                trans.pop(0)
            while trans and all(v == 0 for v in trans[-1]):
                trans.pop()
            sub = [list(row) for row in zip(*trans)]
        return sub

    tl = quadrant(0, cross_row, 0, cross_col)          
    tr = quadrant(0, cross_row, cross_col + 1, w)     
    bl = quadrant(cross_row + 1, h, 0, cross_col)     
    br = quadrant(cross_row + 1, h, cross_col + 1, w) 

    min_h = min(len(tl), len(tr), len(bl), len(br))
    min_w = min(
        len(tl[0]) if tl else 0,
        len(tr[0]) if tr else 0,
        len(bl[0]) if bl else 0,
        len(br[0]) if br else 0,
    )

    def crop(mat):
        return [row[:min_w] for row in mat[:min_h]]

    tl, tr, bl, br = map(crop, (tl, tr, bl, br))

    top = [tl[i] + tr[i] for i in range(min_h)]
    bottom = [bl[i] + br[i] for i in range(min_h)]
    return top + bottom