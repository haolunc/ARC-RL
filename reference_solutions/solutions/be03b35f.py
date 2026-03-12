def transform(grid):

    n = len(grid)            
    k = n // 2               

    tl = [row[:k] for row in grid[:k]]

    rotated = [list(r) for r in zip(*tl)][::-1]

    return rotated