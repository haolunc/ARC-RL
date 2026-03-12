def transform(grid):

    h = len(grid)
    w = len(grid[0]) if h else 0

    for r in range(h - 2):
        for c in range(w - 2):

            all_zero = True
            for dr in range(3):
                for dc in range(3):
                    if grid[r + dr][c + dc] != 0:
                        all_zero = False
                        break
                if not all_zero:
                    break

            if all_zero:
                for dr in range(3):
                    for dc in range(3):
                        grid[r + dr][c + dc] = 1

    return grid