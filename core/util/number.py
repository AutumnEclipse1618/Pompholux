from typing import TypeAlias

from bson import Int64

__all__ = [
    "uint64",
    "Int",
    "tryint",
    "tryint64",
    "int_to_uint64",
    "uint64_to_int",
]


uint64: TypeAlias = Int64
Int: TypeAlias = int | uint64 | Int64


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


def int_to_uint64(n: Int) -> Int64:
    return Int64(int.from_bytes(n.to_bytes(8, byteorder='little', signed=True), byteorder='little', signed=False))


def uint64_to_int(n: Int) -> Int64:
    return Int64(int.from_bytes(n.to_bytes(8, byteorder='little', signed=False), byteorder='little', signed=True))
