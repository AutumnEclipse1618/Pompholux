from typing import TYPE_CHECKING

from .MiscCog import MiscCog

if TYPE_CHECKING:
    from typing import List, Type
    from discord.ext import commands
    from ..MyBot import MyBot


cogs: "List[Type[commands.Cog]]" = [
    ##########
    # Add cogs here
    ##########
    MiscCog,
    ##########
]


async def setup(bot: "MyBot"):
    for cog in cogs:
        await bot.add_cog(cog())
    await bot.load_extension("bot.cog.admin")
