import discord
from discord.ext import commands

class MiscAdminCog(commands.Cog):
    @discord.app_commands.command(description="Make the bot say something in this channel")
    @discord.app_commands.guild_only()
    @discord.app_commands.default_permissions(administrator=True)
    async def botsay(self, ctx: discord.Interaction, text: str):
        await ctx.response.defer(ephemeral=True, thinking=False)
        await ctx.delete_original_response()
        await ctx.channel.send(text, allowed_mentions=discord.AllowedMentions.all())
