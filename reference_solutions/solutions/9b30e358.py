def transform(grid):

    if not grid or not grid[0]:
        return grid

    bg = grid[0][0]

    B = 0
    for row in grid:
        if all(cell == bg for cell in row):
            B += 1
        else:
            break

    pat = grid[B:]               
    P = len(pat)

    if B == 0 or P == 0:
        return grid

    off = B % P

    top = []
    for i in range(B):
        idx = (off + i) % P
        top.append(pat[idx][:])   

    bottom = [row[:] for row in pat]

    return top + bottom