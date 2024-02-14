import tomllib
from typing import Type, TypeVar

import dacite

__all__ = ["load_config"]


T = TypeVar("T")

def load_config(cls: Type[T], filename: str) -> T:
    with open(filename, "rb") as fp:
        dct = tomllib.load(fp)
    return dacite.from_dict(cls, dct)
