import itertools
from typing import Literal, Sequence

import discord
from bson import Int64
from discord.ext import commands

import db.Guilds
from bot.MyViews import FinishableView, ResolvableView, MutexView
from bot.MyModal import MyModal
from bot.error import UserInputWarning
from core.util import tryint, MyFormatter
from core.util.discord import ContentValidation, ContentResult
from db.models.Guild import Autochannel


class AutochannelForm(MyModal, title="Autochannel Options"):
    """Popup to edit guild autochannel settings"""
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

    @staticmethod
    def get_category(category: str, channels: "Sequence[discord.guild.GuildChannel]") -> discord.CategoryChannel:
        return discord.utils.find(
            lambda ch: (ch.id == tryint(category) or ch.name.casefold() == category.casefold()) and isinstance(ch, discord.CategoryChannel),
            channels
        )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        _notify: "discord.guild.GuildChannel | discord.Thread" = discord.utils.find(
            lambda ch: (ch.id == tryint(self.notify.value) or ch.name == self.notify.value) and isinstance(ch, discord.abc.Messageable),
            itertools.chain(interaction.guild.channels, interaction.guild.threads)
        )
        if not _notify:
            raise UserInputWarning(":x: Notification channel must be a valid text channel/thread name and ID")

        try:
            ContentValidation.parse(self.content.value)
        except UserInputWarning:
            raise

        _category = self.get_category(self.category.value, interaction.guild.channels)
        if self.category.value and not _category:
            raise UserInputWarning(":x: Category not valid")

        await db.Guilds.update_autochannel(interaction.guild.id, Autochannel(
            enabled=True,
            notify=Int64(_notify.id),
            content=self.content.value,
            format=self.format.value,
            category=Int64(_category.id) if _category else None
        ))
        await interaction.followup.send("Autochannel enabled", ephemeral=True)


class EditAutochannelNotificationForm(MyModal, title="Edit New Channel"):
    """Popup to edit message for when a user joins"""
    def __init__(self, *, view: "AutochannelNotification", **kwargs):
        super().__init__(**kwargs)
        self.view = view

        self.name = discord.ui.TextInput(label="Channel Name", required=True, default=view.channel_name)
        self.category = discord.ui.TextInput(
            label="Category Name or ID", required=False,
            default=view.category.name if isinstance(view.category, discord.CategoryChannel) else view.category or ""
        )

        self.add_item(self.name).add_item(self.category)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.channel_name = self.name.value.lower().replace(" ", "-")
        category = AutochannelForm.get_category(self.category.value, interaction.guild.channels) \
            or self.category.value \
            or None  # if value is ""
        if isinstance(category, discord.CategoryChannel) and len(category.channels) >= 50:
            raise UserInputWarning(":x: Category full")
        else:
            self.view.category = category
            await self.view.update_message()


class AutochannelNotification(FinishableView, ResolvableView[bool], MutexView):
    """View for message for when a user joins"""
    def __init__(self, autochannel: Autochannel, user: discord.Member, channel_name: str, category: discord.CategoryChannel | str | None):
        super().__init__(timeout=43200)
        self.autochannel = autochannel
        self.user = user
        self.channel_name: str | None = channel_name
        self.category = category

    message: discord.Message

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(":x: You must have manage channels permission", ephemeral=True)
            return False
        return await super().interaction_check(interaction)

    # TODO channel overflow warning?
    default_content = \
        "${USER} has joined, channel \"${CHANNEL}\" will be created\n" \
        "It will be added %{CATEGORY%|to %{NEW_CATEGORY%|a new %}category \"${CATEGORY}\"%|outside of any category%}"

    def generate_content(self) -> ContentResult:
        return ContentValidation.parse(MyFormatter.format(
            self.autochannel.content,
            default=self.default_content,
            user=self.user.mention,
            channel=self.channel_name,
            category=self.category.name if isinstance(self.category, discord.CategoryChannel) else self.category or "",
            new_category=isinstance(self.category, str)
        ))

    async def update_view(self):
        await self.message.edit(view=self)

    async def update_message(self):
        await self.message.edit(**self.generate_content(), allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=True))

    @discord.ui.button(emoji="\u2705", style=discord.ButtonStyle.secondary)  # :white_check_mark:
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.emoji = "\u2714"  # :heavy_check_mark:
        button.style = discord.ButtonStyle.success
        await self.update_view()
        self.set_result(True)
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(emoji="\u270f", style=discord.ButtonStyle.secondary)  # :pencil2:
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = EditAutochannelNotificationForm(view=self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(emoji="\u274c", style=discord.ButtonStyle.secondary)  # :x:
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.channel_name = None
        button.emoji = "\u2716"  # :heavy_multiplication_x:
        button.style = discord.ButtonStyle.danger
        await self.update_view()
        self.set_result(False)
        self.stop()
        await interaction.response.defer()


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
                    (_category := autochannel_ and ctx.guild.get_channel(autochannel_.category))
                    and isinstance(_category, discord.CategoryChannel)
                    else ""
                )
            ))
        else:
            await db.Guilds.enable_autochannel(ctx.guild.id, False)
            await ctx.response.send_message("Autochannel disabled", ephemeral=True)

    @commands.Cog.listener(name="on_member_join")
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        autochannel_ = (await db.Guilds.find(guild.id, ["autochannel"])).autochannel

        if autochannel_ and autochannel_.enabled:
            view = AutochannelNotification(
                autochannel=autochannel_,
                user=member,
                channel_name=MyFormatter.format(autochannel_.format, user=member.name.lower().replace(" ", "-")),
                category=(
                    category_
                    if (
                            autochannel_.category
                            and (category_ := guild.get_channel(autochannel_.category))
                            and isinstance(category_, discord.CategoryChannel)  # noqa
                            and len(category_.channels) < 50
                    )
                    else None
                )
            )
            if not (notify := guild.get_channel(autochannel_.notify)):
                return
            try:
                message = await notify.send(
                    **view.generate_content(),
                    allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=True),
                    view=view
                )
                view.message = message
            except:  # TODO discord.Forbidden | json error | http exception
                pass
            else:
                if await view.when() is True:
                    channel_name = view.channel_name
                    category = view.category
                    if isinstance(category, str):
                        category = await guild.create_category(category, reason="Autochannel")
                    await guild.create_text_channel(channel_name, category=category, reason="Autochannel")


@discord.app_commands.context_menu(name="Join")
@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(administrator=True)
async def join_member(ctx: discord.Interaction, member: discord.Member):
    await ctx.response.send_message("a")
    await (await ctx.original_response()).delete()
    ctx.client.dispatch("member_join", member)
join_member: discord.app_commands.ContextMenu
