def transform(grid):

    h = len(grid)                
    w = len(grid[0]) if h else 0 

    out = [row[:] for row in grid]

    for r in range(h):
        c = 0
        while c < w:
            start = c
            bg = None          

            while c < w:
                val = grid[r][c]
                if val != 2:               
                    if bg is None:
                        bg = val          
                    elif val != bg:
                        break              
                c += 1

            end = c  

            if bg is None:
                continue

            k = sum(1 for i in range(start, end) if grid[r][i] == 2)

            if bg == 8:          
                for i in range(start, end):
                    out[r][i] = 2 if (i - start) < k else bg
            elif bg == 1:        
                for i in range(start, end):
                    out[r][i] = 2 if i >= end - k else bg
            else:

                pass

    return out