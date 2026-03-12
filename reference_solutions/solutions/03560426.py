def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    comps = {}
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val == 0:
                continue
            if val not in comps:
                comps[val] = [r, r, c, c]   
            else:
                mi_r, ma_r, mi_c, ma_c = comps[val]
                comps[val] = [min(mi_r, r), max(ma_r, r), min(mi_c, c), max(ma_c, c)]

    comp_list = []
    for col, (mi_r, ma_r, mi_c, ma_c) in comps.items():
        height = ma_r - mi_r + 1
        width  = ma_c - mi_c + 1
        comp_list.append({
            'color': col,
            'height': height,
            'width': width,
            'min_r': mi_r,
            'min_c': mi_c
        })

    comp_list.sort(key=lambda x: x['min_c'])

    out = [[0 for _ in range(w)] for _ in range(h)]

    cur_top = 0
    cur_left = 0
    for i, comp in enumerate(comp_list):

        for dr in range(comp['height']):
            for dc in range(comp['width']):
                r = cur_top + dr
                c = cur_left + dc
                if 0 <= r < h and 0 <= c < w:
                    out[r][c] = comp['color']

        cur_top = cur_top + comp['height'] - 1   
        cur_left = cur_left + comp['width'] - 1 

    return out