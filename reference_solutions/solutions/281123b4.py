def transform(grid):

    rows = len(grid)            
    cols = len(grid[0])         

    sep = [c for c in range(cols)
           if all(grid[r][c] == 3 for r in range(rows))]

    blocks = []
    start = 0
    for s in sep:

        block = [row[start:s] for row in grid]
        blocks.append(block)
        start = s + 1

    blocks.append([row[start:cols] for row in grid])

    block_width = len(blocks[0][0])   
    out = [[0] * block_width for _ in range(rows)]

    priority = [2, 3, 0, 1]   
    for r in range(rows):
        for c in range(block_width):
            for b in priority:
                val = blocks[b][r][c]
                if val != 0:
                    out[r][c] = val
                    break
    return out