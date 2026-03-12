def transform(grid):

    g = [list(row) for row in grid]
    h, w = len(g), len(g[0])

    blocks = []                     
    in_block = False
    for c in range(w):
        column_has_colour = any(g[r][c] != 0 for r in range(h))
        if column_has_colour and not in_block:

            c_start = c
            in_block = True
        elif not column_has_colour and in_block:

            blocks.append((c_start, c - 1))
            in_block = False
    if in_block:                    
        blocks.append((c_start, w - 1))

    for c_start, c_end in blocks:

        rows_in_block = [
            r for r in range(h)
            if any(g[r][c] != 0 for c in range(c_start, c_end + 1))
        ]

        pattern_rows = [
            r for r in rows_in_block
            if all(g[r][c] != 0 for c in range(c_start, c_end + 1))
        ]
        pattern_rows.sort()

        def pattern_of(row):
            return [g[row][c] for c in range(c_start, c_end + 1)]

        if pattern_rows:

            first_pat = pattern_rows[0]
            pat_len = len(pattern_rows)
            patterns = [pattern_of(r) for r in pattern_rows]

            for r in rows_in_block:

                if all(g[r][c] != 0 for c in range(c_start, c_end + 1)):
                    continue

                nonzeros = [(c, g[r][c]) for c in range(c_start, c_end + 1) if g[r][c] != 0]

                if len(nonzeros) == 1 and nonzeros[0][0] == c_start:
                    left_colour = nonzeros[0][1]

                    if left_colour == patterns[0][0]:

                        pat = patterns[(r - first_pat) % pat_len]
                        for offset, c in enumerate(range(c_start, c_end + 1)):
                            g[r][c] = pat[offset]
                    else:

                        for c in range(c_start, c_end + 1):
                            g[r][c] = left_colour

        else:

            for r in rows_in_block:

                for c in range(c_start, c_end + 1):
                    if g[r][c] != 0:
                        colour = g[r][c]
                        for cc in range(c_start, c_end + 1):
                            g[r][cc] = colour
                        break

    return g