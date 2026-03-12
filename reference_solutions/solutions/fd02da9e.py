def transform(grid):

    n = len(grid)          

    result = [[7 for _ in range(n)] for _ in range(n)]

    patterns = {
        (0, 0): [(1, 1), (1, 2), (2, 1), (2, 2)],          
        (0, n - 1): [(1, -2), (1, -1), (2, -2), (2, -1)], 
        (n - 1, 0): [(-3, 2), (-2, 2), (-1, 3)],          
        (n - 1, n - 1): [(-3, -2), (-2, -2), (-1, -3)],   
    }

    corners = [(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)]
    for r, c in corners:
        colour = grid[r][c]
        if colour == 7:
            continue          

        result[r][c] = 7
        for dr, dc in patterns[(r, c)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                result[nr][nc] = colour

    return result