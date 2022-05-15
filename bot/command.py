from types import MethodType
from typing import TYPE_CHECKING, TypeVar, Any, Dict

from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from .MyBot import MyBot


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
