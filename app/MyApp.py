from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from core.types.Config import Config
    from motor.motor_asyncio import AsyncIOMotorClient
    from bot.MyBot import MyBot


class MyApp:
    config: "Config"
    emoji: Dict[str, str]
    emoji_rev: Dict[str, str]
    db_client: "AsyncIOMotorClient"
    bot: "MyBot"
