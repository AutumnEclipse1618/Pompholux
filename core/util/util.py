from typing import Callable, ParamSpec, TypeVar

__all__ = [
    "predicate_or",
    "predicate_and",
    "predicate_or_async",
    "predicate_and_async",
    "pop_dict",
]


P = ParamSpec('P')
KT = TypeVar("KT")
VT = TypeVar("VT")


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
