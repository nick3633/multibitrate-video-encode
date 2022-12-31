def math_round(num, digits=0):
    if digits == 0:
        return int(num + 0.5)
    else:
        digit_sqr = 10 ** digits
        return int(num * digit_sqr + 0.5) / digit_sqr