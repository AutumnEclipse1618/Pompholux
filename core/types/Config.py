from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """Main App Configuration"""
    Debug: Debug
    Discord: Discord
    Database: Database

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

@dataclass
class Database:
    """MongoDB credentials and related settings"""
    connection: str
