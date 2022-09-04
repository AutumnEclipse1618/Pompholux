from typing import TYPE_CHECKING

import discord

from .Autorole import autorole, AutoroleButtonsView, AutoroleDropdownView, edit_autorole

if TYPE_CHECKING:
    from typing import List, Type
    from discord.ext import commands
    from ...MyBot import MyBot


cogs: "List[Type[commands.Cog]]" = [
    ##########
    # Add cogs here
    ##########

    ##########
]


async def setup(bot: "MyBot"):
    for cog in cogs:
        await bot.add_cog(cog(bot))

    admin_group = discord.app_commands.Group(
        name="admin",
        description="Admin commands",
        guild_only=True,
    )
    admin_group.add_command(autorole)
    bot.tree.add_command(admin_group)

    bot.tree.add_command(edit_autorole)

    bot.add_raw_view(AutoroleButtonsView)
    bot.add_raw_view(AutoroleDropdownView)
