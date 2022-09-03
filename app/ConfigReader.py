import configparser
import re
from typing import List, Type, TypeVar

import dacite

__all__ = ["read_config"]


T = TypeVar("T")


def read_config(cls: Type[T], *files: str) -> T:
    def escape(key: str):
        """Replace all invalid characters with an underscore"""
        return re.sub(r'\W', "_", key, re.ASCII)

    cfg = configparser.ConfigParser(allow_no_value=True, interpolation=configparser.ExtendedInterpolation())
    cfg.optionxform = lambda o: escape(o)

    cfg.read(files)

    config = dacite.from_dict(
        data_class=cls,
        data={escape(k): dict(v) for k, v in cfg.items()},
        config=dacite.Config(
            cast=[int, float],
            type_hooks={
                bool: lambda s: True if s is None else cfg._convert_to_boolean(s),
                List[int]: lambda s: list(map(int, re.split(r'\D+', re.sub(r'(^\D*)|(\D*$)', "", s)))),
                List[str]: lambda s: s.strip("\n").split("\n"),
            },
        ),
    )

    return config
