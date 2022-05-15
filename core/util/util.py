from typing import Callable, ParamSpec, Coroutine, Any

__all__ = [
    "tryint",
    "predicate_or",
    "predicate_and",
    "predicate_or_async",
    "predicate_and_async",
]


P = ParamSpec('P')


def tryint(s: str, *, base: int = 10, default: int | None = None):
    try:
        return int(s, base=base)
    except ValueError:
        return default


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
