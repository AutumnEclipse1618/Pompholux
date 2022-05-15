from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from discord.ext import commands

BotT = TypeVar("BotT", bound="commands.Bot")


class MyCog(Generic[BotT]):
    def __init__(self, bot: BotT):
        self.bot = bot
