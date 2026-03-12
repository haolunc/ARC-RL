def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0

    from collections import defaultdict
    positions = defaultdict(list)
    for r in range(H):
        for c in range(W):
            positions[grid[r][c]].append((r, c))

    def bbox(cells):
        rs = [r for r, _ in cells]
        cs = [c for _, c in cells]
        return min(rs), min(cs), max(rs), max(cs)

    candidate = None
    candidate_mask = None
    cand_top = cand_left = None
    cand_h = cand_w = None

    for color, cells in positions.items():
        if color == 0:
            continue
        if len(cells) < 4:
            continue
        r0, c0, r1, c1 = bbox(cells)
        h = r1 - r0 + 1
        w = c1 - c0 + 1
        area = h * w

        mask = [[0]*w for _ in range(h)]
        for (r, c) in cells:
            mask[r - r0][c - c0] = 1
        cnt = sum(sum(row) for row in mask)

        if cnt == area:
            candidate = color
            candidate_mask = mask
            cand_top, cand_left = r0, c0
            cand_h, cand_w = h, w
            break

        border_count = 2*w + 2*h - 4
        if cnt == border_count:

            ok = True
            for i in range(h):
                for j in range(w):
                    should = 1 if (i == 0 or i == h-1 or j == 0 or j == w-1) else 0
                    if mask[i][j] != should:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                candidate = color
                candidate_mask = mask
                cand_top, cand_left = r0, c0
                cand_h, cand_w = h, w
                break

    if candidate is None:

        return [row[:] for row in grid]

    interior_coords = []
    border_coords = []
    for i in range(cand_h):
        for j in range(cand_w):
            if candidate_mask[i][j] == 1:
                border_coords.append((i, j))
            else:
                interior_coords.append((i, j))

    best_score = None
    best_pos = None
    for top in range(0, H - cand_h + 1):
        for left in range(0, W - cand_w + 1):
            if top == cand_top and left == cand_left:
                continue

            interior_zeros = 0
            border_zeros = 0

            overlap_same_color = False
            for (i, j) in interior_coords:
                if grid[top + i][left + j] == 0:
                    interior_zeros += 1
            for (i, j) in border_coords:
                if grid[top + i][left + j] == 0:
                    border_zeros += 1
                if grid[top + i][left + j] == candidate:
                    overlap_same_color = True

            score = (interior_zeros, border_zeros, -int(overlap_same_color))
            if best_score is None or score > best_score:
                best_score = score
                best_pos = (top, left)

    if best_pos is None:
        return [row[:] for row in grid]

    top, left = best_pos
    out = [row[:] for row in grid]
    for (i, j) in border_coords:
        out[top + i][left + j] = candidate

    return out