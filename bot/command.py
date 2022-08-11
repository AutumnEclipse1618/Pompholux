import logging
from types import MethodType
from typing import TYPE_CHECKING, TypeVar, Any, Dict

from discord import app_commands, Interaction
from discord.ext import commands

from bot.error import UserInputWarning

if TYPE_CHECKING:
    from .MyBot import MyBot


class MyTree(app_commands.CommandTree["MyBot"]):
    async def on_error(self, interaction: Interaction, ex: app_commands.AppCommandError) -> None:
        match ex:
            case app_commands.CommandInvokeError(original=UserInputWarning(message)):
                await interaction.response.send_message(message, ephemeral=True)
            case _:
                await interaction.response.defer()
                # noinspection PyTypeChecker
                command: app_commands.Command | app_commands.ContextMenu | None = interaction.command
                if command is not None and not command._has_any_error_handlers():
                    logging.getLogger("MyBot").error('Ignoring exception in command %r', command.name, exc_info=ex)
                elif command is None:
                    logging.getLogger("MyBot").error('Ignoring exception in command tree', exc_info=ex)


class MyCommand(commands.Command):
    async def dispatch_error(self, ctx: commands.Context["MyBot"], error: commands.CommandError, /) -> None:
        ctx.command_failed = True
        cog = self.cog
        command_handler = None
        cog_handler = None
        bot_handler = lambda c, e: ctx.bot.dispatch('command_error', c, e)
        try:
            coro = self.on_error
        except AttributeError:
            pass
        else:
            injected = commands.core.wrap_callback(coro)
            if cog is not None:
                command_handler = lambda c, e: injected(cog, c, e)
            else:
                command_handler = lambda c, e: injected(c, e)

        if cog is not None:
            local = commands.Cog._get_overridden_method(cog.cog_command_error)
            if local is not None:
                wrapped = commands.core.wrap_callback(local)
                cog_handler = lambda c, e: wrapped(c, e)

        ex = error
        if command_handler is not None:
            try:
                await command_handler(ctx, ex)
            except commands.CommandError as ex_command:
                ex = ex_command
            else:
                return
        if cog_handler is not None:
            try:
                await cog_handler(ctx, ex)
            except commands.CommandError as ex_cog:
                ex = ex_cog
            else:
                return
        bot_handler(ctx, ex)
