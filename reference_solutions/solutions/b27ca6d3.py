def transform(grid):

    import copy

    h = len(grid)
    w = len(grid[0])

    out = copy.deepcopy(grid)

    d4 = [(1,0),(-1,0),(0,1),(0,-1)]

    d8 = [(1,0),(-1,0),(0,1),(0,-1),
           (1,1),(1,-1),(-1,1),(-1,-1)]

    visited = [[False]*w for _ in range(h)]

    for i in range(h):
        for j in range(w):
            if grid[i][j] == 2 and not visited[i][j]:

                comp = [(i,j)]
                visited[i][j] = True
                q = [(i,j)]
                while q:
                    y,x = q.pop(0)
                    for dy,dx in d4:
                        ny,nx = y+dy, x+dx
                        if 0 <= ny < h and 0 <= nx < w:
                            if grid[ny][nx] == 2 and not visited[ny][nx]:
                                visited[ny][nx] = True
                                comp.append((ny,nx))
                                q.append((ny,nx))

                if len(comp) >= 2:
                    for y,x in comp:
                        for dy,dx in d8:
                            ny,nx = y+dy, x+dx
                            if 0 <= ny < h and 0 <= nx < w:
                                if out[ny][nx] == 0:      
                                    out[ny][nx] = 3
    return out