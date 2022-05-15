from typing import TYPE_CHECKING

from core.types.app_abc import AppABC

if TYPE_CHECKING:
    from core.types.Config import Config
    from bot.MyBot import MyBot


class MyApp(AppABC):
    config: "Config"
    bot: "MyBot"

    def run(self):
        self.bot.run(self.config.Discord.token)
