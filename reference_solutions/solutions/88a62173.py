def transform(grid):

    n = len(grid)            
    k = n // 2               
    mid = k                  

    corners = []
    for r, c in [(0, 0), (0, mid + 1), (mid + 1, 0), (mid + 1, mid + 1)]:
        block = [grid[i][c:c + k] for i in range(r, r + k)]
        corners.append(block)

    def block_key(b):
        return tuple(tuple(row) for row in b)

    counts = {}
    for b in corners:
        key = block_key(b)
        counts[key] = counts.get(key, 0) + 1

    for b in corners:
        if counts[block_key(b)] == 1:
            return b

    return corners[0]