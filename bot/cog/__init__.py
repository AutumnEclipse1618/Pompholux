from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Type
    from discord.ext import commands
    from ..MyBot import MyBot
    from ..MyCog import MyCog


cogs: "List[Type[MyCog[MyBot] | commands.Cog]]" = [
    ##########
    # Add cogs here
    ##########
    ##########
]


async def setup(bot: "MyBot"):
    for cog in cogs:
        await bot.add_cog(cog(bot))
    await bot.load_extension("bot.cog.admin")
