import functools
from typing import Optional, Union


def argmin(values: list[Union[int, float]]) -> Optional[Union[int, float]]:
    if len(values) == 0:
        return None
    if len(values) == 1:
        return values[0]
    return functools.reduce(min, values)


def average(values: list[Union[int, float]]) -> Optional[Union[int, float]]:
    if len(values) == 0:
        return None

    if isinstance(values[0], int):
        return int(sum(values) / len(values))
    return sum(values) / len(values)
