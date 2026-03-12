def transform(grid):

    n = len(grid)                 

    block = (n - 4) // 5

    num_blocks = 5

    out = [[0] * block for _ in range(block)]

    for i in range(block):
        for j in range(block):

            values = []
            for br in range(num_blocks):
                for bc in range(num_blocks):
                    r = br * (block + 1) + i   
                    c = bc * (block + 1) + j
                    values.append(grid[r][c])

            out[i][j] = values[0] if all(v == values[0] for v in values) else 1

    return out