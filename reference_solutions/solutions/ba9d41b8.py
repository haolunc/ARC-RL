def transform(grid):

    out = [row[:] for row in grid]

    rows = len(out)
    cols = len(out[0]) if rows else 0
    visited = set()

    for i in range(rows):
        for j in range(cols):
            colour = out[i][j]
            if colour == 0 or (i, j) in visited:
                continue

            right = j
            while right + 1 < cols and out[i][right + 1] == colour:
                right += 1

            bottom = i
            while bottom + 1 < rows:
                if all(out[bottom + 1][k] == colour for k in range(j, right + 1)):
                    bottom += 1
                else:
                    break

            for ii in range(i, bottom + 1):
                for jj in range(j, right + 1):
                    visited.add((ii, jj))

            for ii in range(i + 1, bottom):
                for jj in range(j + 1, right):
                    if (ii - i) % 2 == (jj - j) % 2:
                        out[ii][jj] = 0

    return out