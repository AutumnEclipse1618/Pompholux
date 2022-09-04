import logging
from typing import TYPE_CHECKING, Type

import discord
from discord.ext import commands

from app import app

from .command import MyTree
from .RawView import RawViewStore, RawViewT
from .error import UserInputWarning
from .RawView import RawView

if TYPE_CHECKING:
    import discord.types.interactions


class MyBot(commands.Bot):
    def __init__(self):
        self._raw_view_store = RawViewStore()

        self.my_logger = logging.getLogger("MyBot")

        intents = discord.Intents.default()
        intents.message_content = True
        commands.Bot.__init__(
            self,
            tree_cls=MyTree,
            command_prefix=self.command_prefix,
            help_command=None,
            intents=intents
        )

    @staticmethod
    def command_prefix(bot: "MyBot", message: discord.Message):
        if message.guild is None:
            return commands.when_mentioned_or("")(bot, message)
        else:
            return commands.when_mentioned(bot, message)

    async def setup_hook(self):
        await self.load_extension("bot.commands")

    async def on_ready(self):
        if app.config.Discord.SYNC_COMMANDS:
            if app.config.Debug.SYNC_GUILDS:
                await self._sync_debug_guilds()
            if app.config.Debug.SYNC_GLOBAL:
                await self.tree.sync()
        await self.change_presence(activity=discord.Game("with bubbles"))
        self.my_logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def _sync_debug_guilds(self):
        for guild in map(discord.Object, app.config.Debug.guild):
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_command_error(self, ctx: commands.Context, ex: Exception, /) -> None:
        match ex:
            case UserInputWarning(message):
                await ctx.send(message, reference=ctx.message, mention_author=False)
            case _:
                self.my_logger.error("Ignoring exception in command %s", ctx.command, exc_info=ex)

    async def on_interaction(self, interaction: discord.Interaction):
        # Handle raw view
        if interaction.type == discord.enums.InteractionType.component:
            # These keys are always there for this interaction type
            inner_data: "discord.types.interactions.MessageComponentInteractionData" = interaction.data
            custom_id = inner_data['custom_id']
            component_type: discord.enums.ComponentType = discord.enums.ComponentType(inner_data['component_type'])
            self._raw_view_store.dispatch_raw_view(component_type, custom_id, interaction)

    def add_raw_view(self, view: Type[RawViewT]):
        if not issubclass(view, RawView):
            raise TypeError(f'expected a subclass of RawView not {view!r}')
        self._raw_view_store.add_raw_view(view)

    def remove_raw_view(self, view: Type[RawViewT]):
        if not issubclass(view, RawView):
            raise TypeError(f'expected a subclass of RawView not {view!r}')
        if not self._raw_view_store.remove_raw_view(view):
            raise ValueError(f'{view!r} not in raw view store')

    # noinspection PyUnusedLocal
    async def on_raw_view_error(
            self,
            view: Type[RawViewT],
            component_type: discord.enums.ComponentType,
            custom_id: str,
            interaction: discord.Interaction,
            ex: Exception
    ):
        match ex:
            case UserInputWarning(message):
                await interaction.response.send_message(message, ephemeral=True)
            case _:
                self.my_logger.error("Ignoring exception in raw view %s", view.__name__, exc_info=ex)
                await interaction.response.defer()

    async def on_modal_error(self, modal: discord.ui.Modal, interaction: discord.Interaction, ex: Exception):
        match ex:
            case UserInputWarning(message):
                if not interaction.response.is_done:
                    await interaction.response.send_message(message, ephemeral=True)
                else:
                    await interaction.followup.send(message, ephemeral=True)
            case _:
                self.my_logger.error("Ignoring exception in modal %r:", modal, exc_info=ex)
                if not interaction.response.is_done:
                    await interaction.response.defer()
