from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from core.types.Config import Config
    from bot.MyBot import MyBot


class MyApp:
    config: "Config"
    emoji: Dict[str, str]
    emoji_rev: Dict[str, str]
    bot: "MyBot"
