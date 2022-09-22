from operator import itemgetter
from typing import TypeVar, Sequence

__all__ = [
    "pop_dict",
    "destructure",
]


_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


def pop_dict(dct: dict[_KT, _VT], *keys: _KT) -> dict[_KT, _VT]:
    for key in keys:
        dct.pop(key)
    return dct


def destructure(dct: dict[str, _VT], *keys: str) -> Sequence[_VT]:
    return itemgetter(*keys)(dct)
