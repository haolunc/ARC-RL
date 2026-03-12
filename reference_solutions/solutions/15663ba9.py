def transform(grid):

    from collections import Counter, deque
    h = len(grid)
    w = len(grid[0]) if h else 0

    cnt = Counter(val for row in grid for val in row if val != 0)
    if not cnt:
        return [row[:] for row in grid]          
    shape = cnt.most_common(1)[0][0]

    outer = [[False] * w for _ in range(h)]
    q = deque()
    for i in range(h):
        for j in range(w):
            if (i == 0 or i == h - 1 or j == 0 or j == w - 1) and grid[i][j] == 0:
                outer[i][j] = True
                q.append((i, j))
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while q:
        i, j = q.popleft()
        for di, dj in dirs:
            ni, nj = i + di, j + dj
            if 0 <= ni < h and 0 <= nj < w and not outer[ni][nj] and grid[ni][nj] == 0:
                outer[ni][nj] = True
                q.append((ni, nj))

    out = [row[:] for row in grid]   

    dir_names = ['N', 'S', 'W', 'E']
    dir_vectors = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}

    for i in range(h):
        for j in range(w):
            if grid[i][j] != shape:
                continue

            neigh = set()
            for d, (di, dj) in zip(dir_names, [( -1,0),(1,0),(0,-1),(0,1)]):
                ni, nj = i + di, j + dj
                if 0 <= ni < h and 0 <= nj < w and grid[ni][nj] == shape:
                    neigh.add(d)

            n = len(neigh)

            if n == 1:
                out[i][j] = 2
                continue

            if n == 2 and (('N' in neigh and 'S' in neigh) or ('W' in neigh and 'E' in neigh)):
                continue

            if n == 2:
                empty = set(dir_names) - neigh
                convex = True
                for d in empty:
                    di, dj = dir_vectors[d]
                    ni, nj = i + di, j + dj
                    if 0 <= ni < h and 0 <= nj < w:
                        if not outer[ni][nj]:   
                            convex = False
                            break

                out[i][j] = 4 if convex else 2
                continue

    return out