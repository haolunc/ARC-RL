def transform(grid):

    out = [row[:] for row in grid]

    ones = [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == 8]
    if len(ones) != 2:
        return out  
    (r1, c1), (r2, c2) = ones

    dr = r2 - r1
    dc = c2 - c1
    abs_dr = abs(dr)
    abs_dc = abs(dc)

    def sgn(x):
        return (x > 0) - (x < 0)

    if abs_dr >= abs_dc:
        long = abs_dr
        short = abs_dc
        extra = long - short
        step_r = sgn(dr)
        step_c = sgn(dc)          

        for i in range(1, long):
            r = r1 + i * step_r
            min_h = max(0, i - extra)
            max_h = min(i, short)
            c_min = c1 + min_h * step_c
            c_max = c1 + max_h * step_c
            if out[r][c_min] != 8:
                out[r][c_min] = 3
            if c_max != c_min and out[r][c_max] != 8:
                out[r][c_max] = 3
    else:  
        long = abs_dc
        short = abs_dr
        extra = long - short
        step_c = sgn(dc)
        step_r = sgn(dr)          

        for i in range(1, long):
            c = c1 + i * step_c
            min_v = max(0, i - extra)
            max_v = min(i, short)
            r_min = r1 + min_v * step_r
            r_max = r1 + max_v * step_r
            if out[r_min][c] != 8:
                out[r_min][c] = 3
            if r_max != r_min and out[r_max][c] != 8:
                out[r_max][c] = 3

    return out