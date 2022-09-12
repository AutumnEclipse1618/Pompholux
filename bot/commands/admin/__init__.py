from typing import TYPE_CHECKING

import discord

from .Autorole import AutoroleCog, AutoroleButtonsView, AutoroleDropdownView, edit_autorole
from .Autochannel import AutochannelCog

if TYPE_CHECKING:
    from typing import List, Type
    from discord.ext import commands
    from ...MyBot import MyBot


cogs: "List[Type[commands.Cog]]" = [
    ##########
    # Add cogs here
    ##########
    AutoroleCog,
    AutochannelCog,
    ##########
]


async def setup(bot: "MyBot"):
    for cog in cogs:
        await bot.add_cog(cog())

    bot.tree.add_command(edit_autorole)

    bot.add_raw_view(AutoroleButtonsView)
    bot.add_raw_view(AutoroleDropdownView)
