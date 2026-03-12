def transform(grid):

    R = len(grid)
    C = len(grid[0])

    zero_cells = [(r, c) for r in range(R) for c in range(C) if grid[r][c] == 0]
    if not zero_cells:            
        return [[]]

    r_min = min(r for r, _ in zero_cells)
    r_max = max(r for r, _ in zero_cells)
    c_min = min(c for _, c in zero_cells)
    c_max = max(c for _, c in zero_cells)

    out_h = r_max - r_min + 1
    out_w = c_max - c_min + 1

    def tile_is_consistent(h, w):
        for r in range(R):
            for c in range(C):
                val = grid[r][c]

                if val != 0 and val != grid[r % h][c % w]:
                    return False
        return True

    tile_h = tile_w = None
    for h in range(1, R + 1):
        for w in range(1, C + 1):
            if tile_is_consistent(h, w):
                tile_h, tile_w = h, w
                break
        if tile_h is not None:
            break

    result = [[0] * out_w for _ in range(out_h)]
    for i in range(out_h):
        for j in range(out_w):
            r = r_min + i
            c = c_min + j
            result[i][j] = grid[r % tile_h][c % tile_w]

    return result