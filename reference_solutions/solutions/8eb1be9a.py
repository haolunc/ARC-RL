def transform(grid):

    if not grid:                     
        return []

    h = len(grid)
    w = len(grid[0])

    nz_rows = [i for i, row in enumerate(grid) if any(cell != 0 for cell in row)]

    if not nz_rows:
        return [row[:] for row in grid]

    first = nz_rows[0]               
    block = [grid[i][:] for i in nz_rows]   
    k = len(block)                   

    out = []
    for i in range(h):
        if i in nz_rows:            
            out.append(grid[i][:])
        else:

            idx = (i - first) % k
            out.append(block[idx][:])
    return out