from dataclasses import dataclass

from db.models.types import uint64


@dataclass
class Server:
    _id: uint64
