def transform(grid: list[list[int]]) -> list[list[int]]:
    import math

    h = len(grid)
    w = len(grid[0])

    counts = {}
    for r in range(h):
        for c in range(w):
            col = grid[r][c]
            if col != 0:
                counts[col] = counts.get(col, 0) + 1

    if not counts:
        return grid

    main_colour = max(counts, key=counts.get)

    main_cells = [(r, c) for r in range(h) for c in range(w) if grid[r][c] == main_colour]

    centroid_r = sum(r for r, _ in main_cells) / len(main_cells)
    centroid_c = sum(c for _, c in main_cells) / len(main_cells)

    odd_cells = [(r, c, grid[r][c]) for r in range(h) for c in range(w)
                 if grid[r][c] != 0 and grid[r][c] != main_colour]

    out = [row[:] for row in grid]

    for r, c, col in odd_cells:
        dr = r - centroid_r
        dc = c - centroid_c

        if abs(dr) >= abs(dc):          
            step_r = -1 if dr > 0 else 1   
            step_c = 0
        else:                           
            step_r = 0
            step_c = -1 if dc > 0 else 1   

        nr, nc = r + step_r, c + step_c
        while 0 <= nr < h and 0 <= nc < w:
            if out[nr][nc] == 0:
                out[nr][nc] = col

            nr += step_r
            nc += step_c

    return out