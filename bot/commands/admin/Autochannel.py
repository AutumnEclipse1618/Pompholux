import itertools
from typing import Literal

import discord
from bson import Int64
from discord.ext import commands

import db.Guilds
from bot.MyModal import MyModal
from bot.error import UserInputWarning
from core.util import tryint
from core.util.discord import ContentValidation
from db.models.Guild import Autochannel


class AutochannelForm(MyModal, title="Autochannel Options"):
    def __init__(self, notify: str, content: str, format_: str, category: str):
        super().__init__()
        self.notify = discord.ui.TextInput(
            label="Notification Channel",
            style=discord.TextStyle.short,
            placeholder="Channel name or ID",
            required=True,
            default=notify,
        )
        self.content = discord.ui.TextInput(
            label="Content",
            style=discord.TextStyle.long,
            placeholder="Enter a string or JSON\n(See help page for JSON format)",
            required=True,
            default=content,
        )
        self.format = discord.ui.TextInput(
            label="New Channel Name Format",
            style=discord.TextStyle.short,
            placeholder=None,
            required=True,
            default=format_,
        )
        self.category = discord.ui.TextInput(
            label="Destination Category",
            style=discord.TextStyle.short,
            placeholder="Category name or ID",
            required=False,
            default=category,
        )
        self.add_item(self.notify).add_item(self.content).add_item(self.format).add_item(self.category)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        _notify: discord.guild.GuildChannel | discord.Thread = discord.utils.find(
            lambda ch: (ch.id == tryint(self.notify.value) or ch.name == self.notify.value) and isinstance(ch, discord.abc.Messageable),
            itertools.chain(interaction.guild.channels, interaction.guild.threads)
        )
        if not _notify:
            raise UserInputWarning(":x: Notification channel must be a valid text channel/thread name and ID")

        try:
            await ContentValidation.parse(self.content.value)
        except UserInputWarning:
            raise

        _category: discord.CategoryChannel = discord.utils.find(
            lambda ch: (ch.id == tryint(self.category.value) or ch.name.casefold() == self.category.value.casefold()) and isinstance(ch, discord.CategoryChannel),
            interaction.guild.channels
        )
        if self.category.value and not _category:
            raise UserInputWarning(":x: Category not valid")

        await db.Guilds.update_autochannel(interaction.guild.id, Autochannel(
            enabled=True,
            notify=Int64(_notify.id),
            content=self.content.value,
            format=self.format.value,
            category=Int64(_category.id) if _category else None
        ))
        await interaction.followup.send("Autochannel enabled.", ephemeral=True)


class AutochannelCog(commands.Cog):
    @discord.app_commands.command(description="Configure autochannel options")
    @discord.app_commands.guild_only()
    @discord.app_commands.default_permissions(administrator=True)
    async def autochannel(self, ctx: discord.Interaction, enabled: Literal["Enable", "Disable"] = "Enable"):
        if enabled == "Enable":
            autochannel_ = (await db.Guilds.find(ctx.guild.id, ["autochannel"])).autochannel
            await ctx.response.send_modal(AutochannelForm(
                notify=(
                    _notify.name if
                    (_notify := (autochannel_ and ctx.guild.get_channel_or_thread(autochannel_.notify))) and isinstance(
                        _notify, discord.abc.Messageable)
                    else ctx.channel.name
                ),
                content=(autochannel_ and autochannel_.content) or "",
                format_=(autochannel_ and autochannel_.format) or "",
                category=(
                    _category.name if
                    (_category := autochannel_ and ctx.guild.get_channel(autochannel_.category)) and isinstance(
                        _category, discord.CategoryChannel)
                    else ""
                )
            ))
        else:
            await db.Guilds.enable_autochannel(ctx.guild.id, False)
            await ctx.response.send_message("Autochannel disabled.", ephemeral=True)

    @commands.Cog.listener(name="on_member_join")
    async def on_member_join(self, member: discord.Member):
        autochannel_ = (await db.Guilds.find(member.guild.id, ["autochannel"])).autochannel
        pass
