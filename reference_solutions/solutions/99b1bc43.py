def transform(grid):

    output = []
    for i in range(4):
        top_row = grid[i]
        bottom_row = grid[i + 5]
        out_row = [3 if top_row[j] != (bottom_row[j] // 2) else 0 for j in range(4)]
        output.append(out_row)
    return output