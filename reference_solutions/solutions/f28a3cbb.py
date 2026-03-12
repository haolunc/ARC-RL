def transform(grid):

    from copy import deepcopy

    n = len(grid)

    def reflect_pos(r, c):
        return (n - 1 - r, n - 1 - c)

    def core_color_at_top_left(g):
        c = g[0][0]
        for i in range(3):
            for j in range(3):
                if g[i][j] != c:
                    return None
        return c

    def core_color_at_bottom_right(g):
        c = g[n-1][n-1]
        for i in range(n-3, n):
            for j in range(n-3, n):
                if g[i][j] != c:
                    return None
        return c

    top_color = core_color_at_top_left(grid)
    bot_color = core_color_at_bottom_right(grid)

    colors = set()
    for row in grid:
        colors.update(row)
    bg_color = None
    if top_color is not None and bot_color is not None:
        remaining = colors - {top_color, bot_color}
        if remaining:

            bg_color = next(iter(remaining))
        else:

            from collections import Counter
            cnt = Counter([c for row in grid for c in row])
            bg_color = cnt.most_common(1)[0][0]
    else:

        from collections import Counter
        cnt = Counter([c for row in grid for c in row])
        bg_color = cnt.most_common(1)[0][0]

    out = [[bg_color for _ in range(n)] for _ in range(n)]

    def project_top_left_positions(positions):
        mapped = set()
        for (r, c) in positions:
            if 0 <= r <= 2 and 0 <= c <= 2:
                nr, nc = r, c
            elif 0 <= r <= 2 and c > 2:
                nr, nc = r, 3
            elif 0 <= c <= 2 and r > 2:
                nr, nc = 3, c
            else:

                dr = r - 2
                dc = c - 2
                if dr <= dc:
                    nr, nc = 2, 3
                else:
                    nr, nc = 3, 2
            mapped.add((nr, nc))
        return mapped

    def apply_color_projection(color, mirror=False):
        if color is None:
            return

        poss = []
        for i in range(n):
            for j in range(n):
                if grid[i][j] == color:
                    poss.append((i, j))
        if mirror:

            poss = [reflect_pos(r, c) for (r, c) in poss]
        mapped = project_top_left_positions(poss)  
        if mirror:

            mapped_back = set()
            for (r, c) in mapped:
                rr, cc = reflect_pos(r, c)
                mapped_back.add((rr, cc))
            mapped = mapped_back

        for (r, c) in mapped:
            out[r][c] = color

    apply_color_projection(top_color, mirror=False)

    apply_color_projection(bot_color, mirror=True)

    return out