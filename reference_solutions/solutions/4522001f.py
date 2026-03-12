def transform(grid):

    n = 3                     
    out_n = n * 3             

    pos = [(r, c) for r in range(n) for c in range(n) if grid[r][c] == 3]
    if not pos:               
        return [[0] * out_n for _ in range(out_n)]

    r_min = min(r for r, _ in pos)
    r_max = max(r for r, _ in pos)
    c_min = min(c for _, c in pos)
    c_max = max(c for _, c in pos)

    block_sz = max(r_max - r_min + 1, c_max - c_min + 1) * 2   

    r_mid = (r_min + r_max) / 2.0
    c_mid = (c_min + c_max) / 2.0
    top = r_mid < n / 2.0          
    left = c_mid < n / 2.0         

    if top and left:               
        pr, pc = 0, 0
        opp = (out_n - block_sz - 1, out_n - block_sz - 1)   
    elif top and not left:         
        pr, pc = 0, out_n - block_sz
        opp = (out_n - block_sz - 1, 1)                     
    elif not top and left:         
        pr, pc = out_n - block_sz, 0
        opp = (1, out_n - block_sz - 1)                     
    else:                          
        pr, pc = out_n - block_sz, out_n - block_sz
        opp = (1, 1)                                         

    out = [[0] * out_n for _ in range(out_n)]

    def paint(r0, c0):
        for dr in range(block_sz):
            for dc in range(block_sz):
                out[r0 + dr][c0 + dc] = 3

    paint(pr, pc)          
    paint(*opp)            

    return out