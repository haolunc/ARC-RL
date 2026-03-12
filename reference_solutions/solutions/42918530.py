def transform(grid):

    from copy import deepcopy
    H = len(grid)
    W = len(grid[0]) if H>0 else 0
    g = deepcopy(grid)

    blocks = []  
    visited = [[False]*W for _ in range(H)]
    for r in range(H-4):
        for c in range(W-4):
            col = g[r][c]
            if col == 0:
                continue

            ok = True
            for i in range(5):
                for j in range(5):
                    if i==0 or i==4 or j==0 or j==4:
                        if g[r+i][c+j] != col:
                            ok = False
                            break
                if not ok:
                    break
            if not ok:
                continue

            overlap = False
            for i in range(5):
                for j in range(5):
                    if visited[r+i][c+j]:
                        overlap = True
                        break
                if overlap:
                    break
            if overlap:
                continue

            for i in range(5):
                for j in range(5):
                    visited[r+i][c+j] = True
            blocks.append((r,c,col))

    color_positions = {}
    for (r,c,col) in blocks:
        posset = color_positions.setdefault(col, set())
        for i in range(5):
            for j in range(5):
                if g[r+i][c+j] == col:
                    posset.add((i,j))

    out = deepcopy(g)
    for (r,c,col) in blocks:
        posset = color_positions.get(col, set())
        for (i,j) in posset:
            out[r+i][c+j] = col
    return out