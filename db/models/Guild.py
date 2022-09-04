import dataclasses
from dataclasses import dataclass

from db.models.types import uint64


@dataclass
class Autochannel:
    notify: uint64 = None
    content: str = None
    format: str = None
    category: uint64 = None


@dataclass
class Guild:
    _id: uint64
    autochannel: Autochannel = dataclasses.field(default_factory=Autochannel)
