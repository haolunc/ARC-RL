def transform(grid: list[list[int]]) -> list[list[int]]:
    def rotate90(A: list[list[int]]) -> list[list[int]]:

        return [list(row) for row in zip(*A[::-1])]

    def rotate180(A: list[list[int]]) -> list[list[int]]:
        return [row[::-1] for row in A[::-1]]

    NW = grid

    NE = rotate90(NW)

    SE = rotate180(NW)

    SW = rotate90(rotate180(NW))

    top = [nw_row + ne_row for nw_row, ne_row in zip(NW, NE)]
    bottom = [sw_row + se_row for sw_row, se_row in zip(SW, SE)]
    return top + bottom