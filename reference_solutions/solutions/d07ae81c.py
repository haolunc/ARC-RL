def transform(grid):

    import copy

    h = len(grid)
    w = len(grid[0])
    out = copy.deepcopy(grid)

    from collections import Counter, defaultdict
    cnt = Counter(c for row in grid for c in row)

    special_candidates = {c for c, n in cnt.items() if n < 20}

    special_to_region = {}
    for r in range(h):
        for c in range(w):
            col = grid[r][c]
            if col in special_candidates:
                neigh = []
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < h and 0 <= nc < w:
                        neigh.append(grid[nr][nc])
                if neigh:

                    region = max(set(neigh), key=neigh.count)
                    special_to_region[col] = region

    region_to_special = {}
    for sp, rg in special_to_region.items():
        region_to_special[rg] = sp

    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]   

    for sp, region in special_to_region.items():

        positions = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == sp]
        for (sr, sc) in positions:
            for dr, dc in dirs:
                r, c = sr + dr, sc + dc
                while 0 <= r < h and 0 <= c < w:
                    orig = grid[r][c]

                    new_col = region_to_special.get(orig, None)
                    if new_col is not None:
                        out[r][c] = new_col

                    r += dr
                    c += dc

    return out