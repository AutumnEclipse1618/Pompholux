from itertools import pairwise

__all__ = [
    "triplewise",
]


def triplewise(iterable):
    """Return overlapping triplets from an iterable"""
    # triplewise('ABCDEFG') -> ABC BCD CDE DEF EFG
    for (a, _), (b, c) in pairwise(pairwise(iterable)):
        yield a, b, c
