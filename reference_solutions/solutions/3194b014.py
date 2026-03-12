def transform(grid):

    n = len(grid)
    m = len(grid[0])

    colours = set()
    for row in grid:
        colours.update(row)

    def total_count(c):
        return sum(row.count(c) for row in grid)

    best_colour = None
    best_side = -1

    for c in colours:

        dp = [[0] * m for _ in range(n)]
        max_side_c = 0
        for i in range(n):
            for j in range(m):
                if grid[i][j] == c:
                    if i == 0 or j == 0:
                        dp[i][j] = 1
                    else:
                        dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
                    if dp[i][j] > max_side_c:
                        max_side_c = dp[i][j]

        if max_side_c > best_side:
            best_side = max_side_c
            best_colour = c
        elif max_side_c == best_side and best_colour is not None:
            if total_count(c) > total_count(best_colour):
                best_colour = c

    return [[best_colour] * 3 for _ in range(3)]