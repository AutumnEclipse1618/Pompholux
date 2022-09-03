from typing import TypeAlias, TypeVar, Type, Any, List, Dict

import dacite

MongoProjection: TypeAlias = List[str] | Dict[str, bool]
uint64: TypeAlias = int


T = TypeVar("T")


def from_dict(type_: Type[T], data: dict[str, Any]) -> T:
    return dacite.from_dict(
        type_,
        data,
        dacite.Config(
            type_hooks={
                uint64: lambda i: int(i) & 0xFFFFFFFFFFFFFFFF,
            }
        )
    )
