def transform(grid):

    h = len(grid)
    w = len(grid[0])
    best = None                 

    for top in range(h - 2):                
        for bottom in range(top + 2, h):
            for left in range(w - 2):      
                for right in range(left + 2, w):
                    colour = grid[top][left]

                    if any(grid[top][c] != colour for c in range(left, right + 1)):
                        continue

                    if any(grid[bottom][c] != colour for c in range(left, right + 1)):
                        continue

                    if any(grid[r][left] != colour for r in range(top, bottom + 1)):
                        continue

                    if any(grid[r][right] != colour for r in range(top, bottom + 1)):
                        continue

                    area = (bottom - top + 1) * (right - left + 1)
                    if best is None or area > best[0]:
                        best = (area, top, left, bottom, right)

    _, top, left, bottom, right = best
    interior = [row[left + 1: right] for row in grid[top + 1: bottom]]
    return interior