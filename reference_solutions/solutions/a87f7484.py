def transform(grid):

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    best_block = None
    best_count = -1

    for i in range(0, rows, 3):
        for j in range(0, cols, 3):

            block = [grid[i + r][j:j + 3] for r in range(3)]

            cnt = sum(cell != 0 for row in block for cell in row)

            if cnt > best_count:
                best_count = cnt
                best_block = block

    return best_block