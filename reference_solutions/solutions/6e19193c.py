def transform(grid):

    rows, cols = len(grid), len(grid[0])

    out = [row[:] for row in grid]

    orth = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(rows):
        for c in range(cols):
            col = grid[r][c]
            if col == 0:
                continue

            neigh = []
            for dr, dc in orth:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == col:
                    neigh.append((dr, dc))

            if len(neigh) != 2:
                continue

            dr_ext = neigh[0][0] + neigh[1][0]
            dc_ext = neigh[0][1] + neigh[1][1]

            step = 1
            while True:
                nr = r + dr_ext * step
                nc = c + dc_ext * step
                if not (0 <= nr < rows and 0 <= nc < cols):
                    break

                if step == 1:
                    step += 1
                    continue

                if grid[nr][nc] != 0:
                    break
                out[nr][nc] = col
                step += 1

    return out