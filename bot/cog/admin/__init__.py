from typing import TYPE_CHECKING

from .AutoroleCog import AutoroleCog, AutoroleButtonsView, AutoroleDropdownView, edit_autorole

if TYPE_CHECKING:
    from typing import List, Type
    from discord.ext import commands
    from ...MyBot import MyBot
    from ...MyCog import MyCog


cogs: "List[Type[MyCog[MyBot] | commands.Cog]]" = [
    ##########
    # Add cogs here
    ##########
    AutoroleCog,
    ##########
]


async def setup(bot: "MyBot"):
    for cog in cogs:
        await bot.add_cog(cog(bot))
    bot.tree.add_command(edit_autorole)
    bot.add_raw_view(AutoroleButtonsView)
    bot.add_raw_view(AutoroleDropdownView)
