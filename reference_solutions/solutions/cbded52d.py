def transform(grid):

    block_h = block_w = 2      
    sep = 1                    
    nb = 3                     

    for br in range(nb):                     
        base_r = br * (block_h + sep)
        for dr in (0, 1):
            for dc in (0, 1):
                left  = grid[base_r + dr][0 * (block_w + sep) + dc]
                right = grid[base_r + dr][2 * (block_w + sep) + dc]
                if left == right and left not in (0, 1):
                    grid[base_r + dr][1 * (block_w + sep) + dc] = left

    for bc in range(nb):                     
        base_c = bc * (block_w + sep)
        for dr in (0, 1):
            for dc in (0, 1):
                top    = grid[0 * (block_h + sep) + dr][base_c + dc]
                bottom = grid[2 * (block_h + sep) + dr][base_c + dc]
                if top == bottom and top not in (0, 1):
                    grid[1 * (block_h + sep) + dr][base_c + dc] = top

    return grid