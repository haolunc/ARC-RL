def transform(grid):

    A = grid

    A_hor = [row[::-1] for row in A]

    A_vert = A[::-1]

    A_rot180 = [row[::-1] for row in A_vert]

    top = [A[i] + A_hor[i] for i in range(3)]

    bottom = [A_vert[i] + A_rot180[i] for i in range(3)]
    return top + bottom