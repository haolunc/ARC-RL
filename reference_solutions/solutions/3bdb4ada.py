def transform(grid):

    g = [row[:] for row in grid]
    if not g:
        return g
    R = len(g)
    C = len(g[0])

    for i in range(R - 2):  
        j = 0
        while j < C:
            c = g[i][j]
            if c != 0 and g[i+1][j] == c and g[i+2][j] == c:

                start = j
                k = j
                while k < C and g[i][k] == c and g[i+1][k] == c and g[i+2][k] == c:
                    k += 1
                end = k - 1

                for col in range(start, end + 1):
                    g[i+1][col] = c if ((col - start) % 2 == 0) else 0
                j = k  
            else:
                j += 1
    return g