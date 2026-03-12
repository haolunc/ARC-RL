def transform(grid):

    h, w = len(grid), len(grid[0])

    out = [row[:] for row in grid]

    colors = {v for row in grid for v in row if v != 0}

    for color in colors:

        positions = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == color]

        block = set()
        pos_set = set(positions)
        for r, c in positions:
            if (r + 1, c) in pos_set and (r, c + 1) in pos_set and (r + 1, c + 1) in pos_set:
                block = {(r, c), (r + 1, c), (r, c + 1), (r + 1, c + 1)}
                break

        arms = [p for p in positions if p not in block]

        for ar, ac in arms:

            adj = None
            for br, bc in block:
                if max(abs(ar - br), abs(ac - bc)) == 1:
                    adj = (br, bc)
                    break
            if adj is None:
                continue  

            dr = ar - adj[0]
            dc = ac - adj[1]

            nr, nc = ar + dr, ac + dc
            while 0 <= nr < h and 0 <= nc < w:
                out[nr][nc] = color
                nr += dr
                nc += dc

    return out