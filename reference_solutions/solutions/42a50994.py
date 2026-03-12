def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    result = [[0] * w for _ in range(h)]

    for r in range(h):
        for c in range(w):
            colour = grid[r][c]
            if colour == 0:
                continue          
            keep = False
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == colour:
                        keep = True
                        break
                if keep:
                    break
            if keep:
                result[r][c] = colour

    return result