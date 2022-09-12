import dataclasses
from typing import Optional

from db.models.types import uint64


@dataclasses.dataclass
class Autochannel:
    enabled: bool
    notify: uint64 = None
    content: str = None
    format: str = None
    category: Optional[uint64] = None


@dataclasses.dataclass
class Guild:
    _id: uint64
    autochannel: Optional[Autochannel] = None
