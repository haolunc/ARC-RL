def transform(grid):

    n = len(grid)
    if n % 2 != 0:
        raise ValueError("Number of columns must be even")
    half = n // 2

    out = []
    for i in range(half):
        left = grid[i]          
        right = grid[i + half]  

        merged = [4 if (left[row] != 0 or right[row] != 0) else 0 for row in range(4)]
        out.append(merged)

    return out