from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from bot.MyCog import MyCog

if TYPE_CHECKING:
    import discord.types.interactions
    # noinspection PyUnresolvedReferences
    from ..MyBot import MyBot


class MiscCog(MyCog["MyBot"], commands.Cog):
    @discord.app_commands.command(description="Link to wiki")
    async def help(self, ctx: discord.Interaction):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="RTFM", emoji="\U0001F4DD",
            url="https://github.com/AutumnEclipse1618/Pompholux/wiki",
        ))
        await ctx.response.send_message(view=view, ephemeral=True)
