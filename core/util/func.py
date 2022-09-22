from functools import reduce
from typing import Callable, ParamSpec, TypeVar

__all__ = [
    "predicate_or",
    "predicate_and",
    "predicate_or_async",
    "predicate_and_async",
    "compose",
]


_P = ParamSpec("_P")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


def predicate_or(*predicates: Callable[_P, bool]) -> Callable[_P, bool]:
    return lambda *args, **kwargs: any(pred(*args, **kwargs) for pred in predicates)


def predicate_and(*predicates: Callable[_P, bool]) -> Callable[_P, bool]:
    return lambda *args, **kwargs: all(pred(*args, **kwargs) for pred in predicates)


def predicate_or_async(*predicates):
    async def _lambda(*args, **kwargs):
        return any(await pred(*args, **kwargs) for pred in predicates)
    return _lambda


def predicate_and_async(*predicates):
    async def _lambda(*args, **kwargs):
        return all(await pred(*args, **kwargs) for pred in predicates)

    return _lambda


def compose(funcs: list[Callable[[_VT], _VT]], v: _VT) -> _VT:
    return reduce(lambda acc, curr: curr(acc), funcs, v)
