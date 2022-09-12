import dataclasses
from typing import TypeAlias, TypeVar, Type, Any, List, Dict

from bson import Int64
import dacite

from core.util import int_to_uint64, uint64_to_int

uint64: TypeAlias = Int64
Int: TypeAlias = int | uint64 | Int64
MongoProjection: TypeAlias = List[str] | Dict[str, bool]
T = TypeVar("T")


def from_dict(type_: Type[T], data: dict[str, Any]) -> T:
    from_dict_type_hooks = {
        uint64: int_to_uint64,
    }

    return dacite.from_dict(
        type_,
        data,
        dacite.Config(
            type_hooks=from_dict_type_hooks
        )
    )


def asdict(obj: Any) -> dict:
    asdict_type_hooks = {
        uint64: uint64_to_int
    }

    def asdict_factory(data: list[tuple[str, Any]]) -> dict:
        return dict((k, asdict_type_hooks.get(type(v), lambda v: v)(v)) for (k, v) in data)
    return dataclasses.asdict(obj, dict_factory=asdict_factory)
