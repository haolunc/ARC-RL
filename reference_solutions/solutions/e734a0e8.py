def transform(grid):
    from collections import Counter
    import copy

    h = len(grid)
    w = len(grid[0]) if h>0 else 0

    sep_rows = [r for r in range(h) if all(grid[r][c]==0 for c in range(w))]
    sep_cols = [c for c in range(w) if all(grid[r][c]==0 for r in range(h))]

    non_sep_rows = [r for r in range(h) if r not in sep_rows]
    non_sep_cols = [c for c in range(w) if c not in sep_cols]

    def group_contiguous(indices):
        runs = []
        if not indices:
            return runs
        start = indices[0]
        prev = indices[0]
        for idx in indices[1:]:
            if idx == prev + 1:
                prev = idx
            else:
                runs.append((start, prev))
                start = idx
                prev = idx
        runs.append((start, prev))
        return runs

    row_runs = group_contiguous(non_sep_rows)
    col_runs = group_contiguous(non_sep_cols)

    tiles = []
    for rr in row_runs:
        for rc in col_runs:
            r0, r1 = rr
            c0, c1 = rc
            tiles.append((r0, r1, c0, c1))

    if not tiles:
        return grid

    cnt = Counter()
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 0:
                cnt[v] += 1

    if not cnt:
        return grid
    bg_color, _ = cnt.most_common(1)[0]

    source_tile = None
    for (r0, r1, c0, c1) in tiles:
        found = False
        for r in range(r0, r1+1):
            for c in range(c0, c1+1):
                v = grid[r][c]
                if v != 0 and v != bg_color:
                    found = True
                    break
            if found:
                break
        if found:

            tile = [row[c0:c1+1] for row in grid[r0:r1+1]]
            source_tile = (r0, r1, c0, c1, tile)
            break

    if source_tile is None:
        return grid

    _, r1_s, _, c1_s, tile_pattern = source_tile
    tile_h = len(tile_pattern)
    tile_w = len(tile_pattern[0])

    out = copy.deepcopy(grid)

    for (r0, r1, c0, c1) in tiles:

        tr_h = r1 - r0 + 1
        tr_w = c1 - c0 + 1

        center_r = r0 + (tr_h // 2)
        center_c = c0 + (tr_w // 2)
        if grid[center_r][center_c] == 0:

            for i in range(min(tr_h, tile_h)):
                for j in range(min(tr_w, tile_w)):
                    out[r0 + i][c0 + j] = tile_pattern[i][j]

    return out