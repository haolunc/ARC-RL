def transform(grid):

    N = len(grid)
    if N == 0:
        return []                     

    block_size = N // 3

    result = [[0 for _ in range(3)] for _ in range(3)]

    for i, row in enumerate(grid):
        for j, val in enumerate(row):
            if val != 0:
                br = i // block_size   
                bc = j // block_size   
                result[br][bc] = val

    return result