def transform(grid):

    H = len(grid)
    W = len(grid[0]) if H else 0

    cols5 = set()
    rows5 = set()
    for r in range(H):
        for c in range(W):
            if grid[r][c] == 5:
                cols5.add(c)
                rows5.add(r)

    if not cols5:
        return []

    c_min = min(cols5)
    c_max = max(cols5)

    r_min = min(rows5)
    r_max = max(rows5)

    r_start = max(0, r_min - 1)          
    r_end   = min(H - 1, r_max + 1)      

    out = []
    for r in range(r_start, r_end + 1):
        out.append(grid[r][c_min:c_max + 1])

    return out