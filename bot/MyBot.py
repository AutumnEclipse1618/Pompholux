import sys
import traceback
from typing import TYPE_CHECKING, Type

import discord
from discord.ext import commands

from core.types.app_abc import ComponentABC

from .RawView import RawViewStore, RawViewT
from .error import UserInputWarning
from .RawView import RawView

if TYPE_CHECKING:
    import discord.types.interactions
    from app.MyApp import MyApp


class MyBot(ComponentABC["MyApp"], commands.Bot):
    def __init__(self, app: "MyApp"):
        ComponentABC.__init__(self, app)
        self._raw_view_store = RawViewStore()

        intents = discord.Intents.default()
        intents.message_content = True
        commands.Bot.__init__(
            self,
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
        await self.load_extension("bot.cog")

    async def on_ready(self):
        if self.app.config.Discord.SYNC_COMMANDS:
            if self.app.config.Debug.SYNC_GUILDS:
                await self._sync_debug_guilds()
            if self.app.config.Debug.SYNC_GLOBAL:
                await self.tree.sync()
        await self.change_presence(activity=discord.Game("with bubbles"))
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def _sync_debug_guilds(self):
        for guild in map(discord.Object, self.app.config.Debug.guild):
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_command_error(self, ctx: commands.Context, ex: Exception, /) -> None:
        match ex:
            case UserInputWarning(message):
                await ctx.send(message, reference=ctx.message, mention_author=False)
            case _:
                if self.app.config.Debug.DEBUG:
                    print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
                    traceback.print_exception(type(ex), ex, ex.__traceback__, file=sys.stderr)

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
                if self.app.config.Debug.DEBUG:
                    print(f'Ignoring exception in raw view {view.__name__}:', file=sys.stderr)
                    traceback.print_exception(ex.__class__, ex, ex.__traceback__, file=sys.stderr)
                await interaction.response.defer()
