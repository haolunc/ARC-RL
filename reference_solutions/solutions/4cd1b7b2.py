def transform(grid):

    N = len(grid)

    all_vals = set(range(1, N + 1))

    empties = [(r, c) for r in range(N) for c in range(N) if grid[r][c] == 0]

    def solve(idx):

        if idx == len(empties):

            return True

        r, c = empties[idx]

        used = {grid[r][j] for j in range(N) if grid[r][j] != 0}
        used.update({grid[i][c] for i in range(N) if grid[i][c] != 0})

        for v in all_vals - used:
            grid[r][c] = v
            if solve(idx + 1):
                return True
            grid[r][c] = 0          

        return False               

    solve(0)
    return grid