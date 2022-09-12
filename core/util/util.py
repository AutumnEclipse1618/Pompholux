from typing import Callable, ParamSpec, Coroutine, Any, TypeVar

from bson import Int64

__all__ = [
    "tryint",
    "tryint64",
    "int_to_uint64",
    "uint64_to_int",
    "predicate_or",
    "predicate_and",
    "predicate_or_async",
    "predicate_and_async",
    "pop_dict",
]


P = ParamSpec('P')
KT = TypeVar("KT")
VT = TypeVar("VT")


def tryint(s: str, *, base: int = 10, default: int | None = None):
    try:
        return int(s, base=base)
    except ValueError:
        return default


def tryint64(s: str, *, base: int = 10, default: Int64 | None = None):
    try:
        return Int64(s, base=base)
    except ValueError:
        return default


def int_to_uint64(n: int | Int64) -> Int64:
    return Int64(int.from_bytes(n.to_bytes(8, byteorder='little', signed=True), byteorder='little', signed=False))


def uint64_to_int(n: int | Int64) -> Int64:
    return Int64(int.from_bytes(n.to_bytes(8, byteorder='little', signed=False), byteorder='little', signed=True))


def predicate_or(*predicates: Callable[P, bool]) -> Callable[P, bool]:
    return lambda *args, **kwargs: any(pred(*args, **kwargs) for pred in predicates)


def predicate_and(*predicates: Callable[P, bool]) -> Callable[P, bool]:
    return lambda *args, **kwargs: all(pred(*args, **kwargs) for pred in predicates)


def predicate_or_async(*predicates):
    async def _lambda(*args, **kwargs):
        return any(await pred(*args, **kwargs) for pred in predicates)
    return _lambda


def predicate_and_async(*predicates):
    async def _lambda(*args, **kwargs):
        return all(await pred(*args, **kwargs) for pred in predicates)

    return _lambda


def pop_dict(dct: dict[KT, VT], *keys: KT) -> dict[KT, VT]:
    for key in keys:
        dct.pop(key)
    return dct
