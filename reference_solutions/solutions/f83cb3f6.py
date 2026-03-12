def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    row_counts = [sum(1 for v in grid[r] if v == 8) for r in range(h)]
    col_counts = [sum(1 for r in range(h) if grid[r][c] == 8) for c in range(w)]

    if max(row_counts) >= max(col_counts):

        line_idx = row_counts.index(max(row_counts))
        line_cols = [c for c in range(w) if grid[line_idx][c] == 8]

        out = [[0] * w for _ in range(h)]
        for c in line_cols:
            out[line_idx][c] = 8

        for c in line_cols:

            for r in range(line_idx):
                v = grid[r][c]
                if v != 0 and v != 8:
                    out[line_idx - 1][c] = v
                    break        

            for r in range(line_idx + 1, h):
                v = grid[r][c]
                if v != 0 and v != 8:
                    out[line_idx + 1][c] = v
                    break
    else:

        line_idx = col_counts.index(max(col_counts))
        line_rows = [r for r in range(h) if grid[r][line_idx] == 8]

        out = [[0] * w for _ in range(h)]
        for r in line_rows:
            out[r][line_idx] = 8

        for r in line_rows:

            for c in range(line_idx):
                v = grid[r][c]
                if v != 0 and v != 8:
                    out[r][line_idx - 1] = v
                    break

            for c in range(line_idx + 1, w):
                v = grid[r][c]
                if v != 0 and v != 8:
                    out[r][line_idx + 1] = v
                    break

    return out