def transform(grid):

    H = len(grid)
    W = len(grid[0])

    row_info = []
    for r in range(H):
        s = {grid[r][c] for c in range(W) if grid[r][c] != 0}
        if s:                     
            row_info.append((r, frozenset(s)))

    row_groups = []
    i = 0
    while i < len(row_info):
        r_start, cur_set = row_info[i]
        r_end = r_start
        j = i + 1
        while j < len(row_info) and row_info[j][1] == cur_set and              row_info[j][0] == r_end + 1:
            r_end = row_info[j][0]
            j += 1
        row_groups.append((r_start, r_end))
        i = j

    col_info = []
    for c in range(W):
        s = {grid[r][c] for r in range(H) if grid[r][c] != 0}
        if s:
            col_info.append((c, frozenset(s)))

    col_groups = []
    i = 0
    while i < len(col_info):
        c_start, cur_set = col_info[i]
        c_end = c_start
        j = i + 1
        while j < len(col_info) and col_info[j][1] == cur_set and              col_info[j][0] == c_end + 1:
            c_end = col_info[j][0]
            j += 1
        col_groups.append((c_start, c_end))
        i = j

    result = []
    for r0, r1 in row_groups:
        row_vals = []
        for c0, c1 in col_groups:
            freq = {}
            for r in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    v = grid[r][c]
                    if v != 0:
                        freq[v] = freq.get(v, 0) + 1
            if not freq:
                colour = 0
            else:
                max_cnt = max(freq.values())

                colour = min(k for k, v in freq.items() if v == max_cnt)
            row_vals.append(colour)

        row_vals.reverse()
        result.append(row_vals)

    return result