def transform(grid):

    rows = len(grid)
    cols = len(grid[0])

    block_h = rows // 3

    for b in range(3):

        block = [grid[r][:] for r in range(b * block_h, (b + 1) * block_h)]

        symmetric = True
        for i in range(block_h):
            for j in range(block_h):
                if block[i][j] != block[j][i]:
                    symmetric = False
                    break
            if not symmetric:
                break
        if not symmetric:
            return block

    return []