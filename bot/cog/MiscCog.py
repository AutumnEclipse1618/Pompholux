import discord
from discord.ext import commands

import db.Servers


class MiscCog(commands.Cog):
    @discord.app_commands.command(description="Link to wiki")
    async def help(self, ctx: discord.Interaction):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="RTFM", emoji="\U0001F4DD",
            url="https://github.com/AutumnEclipse1618/Pompholux/wiki",
        ))
        await ctx.response.send_message(view=view, ephemeral=True)

    @discord.app_commands.command(description="foo")
    async def foo(self, ctx: discord.Interaction):
        await ctx.response.send_message(await db.Servers.find_one(ctx.guild_id), ephemeral=True)
