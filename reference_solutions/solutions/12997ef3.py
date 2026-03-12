def transform(grid):

    def find_coords(color):
        return [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == color]

    from collections import Counter
    flat = [v for row in grid for v in row if v != 0]
    if not flat:                     
        return []
    cnt = Counter(flat)

    ref_color = min((c for c in cnt if cnt[c] == max(cnt.values())), key=lambda x: x)

    ref_coords = find_coords(ref_color)
    min_r = min(r for r, _ in ref_coords)
    max_r = max(r for r, _ in ref_coords)
    min_c = min(c for _, c in ref_coords)
    max_c = max(c for _, c in ref_coords)

    ph = max_r - min_r + 1          
    pw = max_c - min_c + 1          

    mask = [[0] * pw for _ in range(ph)]
    for r, c in ref_coords:
        mask[r - min_r][c - min_c] = 1

    other_colors = [c for c in cnt if c != ref_color]

    reps = {}
    for color in other_colors:
        r, c = find_coords(color)[0]   
        reps[color] = (r, c)

    rows_set = sorted({r for r, _ in reps.values()})
    cols_set = sorted({c for _, c in reps.values()})

    row_index = {r: i for i, r in enumerate(rows_set)}
    col_index = {c: i for i, c in enumerate(cols_set)}

    out_rows = len(rows_set) * ph
    out_cols = len(cols_set) * pw

    out = [[0] * out_cols for _ in range(out_rows)]

    for color, (r, c) in reps.items():
        br = row_index[r]          
        bc = col_index[c]          
        base_r = br * ph
        base_c = bc * pw
        for i in range(ph):
            for j in range(pw):
                if mask[i][j]:
                    out[base_r + i][base_c + j] = color

    return out