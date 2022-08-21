from typing import TYPE_CHECKING, Dict

from core.types.app_abc import AppABC

if TYPE_CHECKING:
    from core.types.Config import Config
    from bot.MyBot import MyBot


class MyApp(AppABC):
    config: "Config"
    emoji: Dict[str, str]
    emoji_rev: Dict[str, str]
    bot: "MyBot"

    def run(self):
        self.bot.run(self.config.Discord.token)
