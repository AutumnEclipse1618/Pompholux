from dataclasses import dataclass, field
from typing import List


@dataclass
class Versions:
    """Bot and library versions"""
    version: str
    python: str
    discord_py: str
    motor: str
    dacite: str


@dataclass
class Debug:
    """Debug Options"""
    DEBUG: bool = False
    SYNC_GLOBAL: bool = True
    SYNC_GUILDS: bool = False
    guild: List[int] = None


@dataclass
class Discord:
    """Discord credentials and related settings"""
    token: str
    SYNC_COMMANDS: bool = True
    prefix: List[str] = field(default_factory=list)


@dataclass
class Database:
    """MongoDB credentials and related settings"""
    connection: str


@dataclass
class Config:
    """Main App Configuration"""
    Versions: Versions
    Debug: Debug
    Discord: Discord
    Database: Database
