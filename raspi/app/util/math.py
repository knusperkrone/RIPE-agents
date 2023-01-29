import functools

def argmin(values: list) -> int or None:
    if len (values) == 0:
        return None
    if len (values) == 1:
        return values[0]
    return functools.reduce(min, values)

def average(values: list) -> int or None:
    if len(values) == 0:
        return None
    return sum(values) / len(values)