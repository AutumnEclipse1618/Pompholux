import asyncio
from typing import Generic, TypeVar

import discord


class FinishableView(discord.ui.View):
    """
    Has a single callback that handles being stopped and timed out
    By default disables all message components on timeout/finish
    """
    # https://discordpy.readthedocs.io/en/latest/faq.html#how-can-i-disable-all-items-on-timeout

    message: discord.Message

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._View__stopped.add_done_callback(lambda f: asyncio.create_task(self.on_finished(), name=f'mybot-view-finished-{self.id}'))  # noqa

    async def on_finished(self):
        await self.disable()

    async def disable(self):
        for item in self.children:
            item.disabled = True

        try:
            await self.message.edit(view=self)
        except AttributeError:
            pass


V = TypeVar("V")


class ResolvableView(Generic[V], discord.ui.View):
    """Has an awaitable custom result"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._result: V = None
        self._deferred: asyncio.Future[V] = asyncio.get_running_loop().create_future()
        self._View__stopped.add_done_callback(lambda f: self._deferred.set_result(self._result))  # noqa

    def set_result(self, value: V):
        self._result = value

    async def when(self) -> V | None:
        return await self._deferred


class MutexView(discord.ui.View):
    """Allows only one interaction to go through at a time"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = asyncio.Lock()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return not self.is_finished()

    async def _scheduled_task(self, *args):
        async with self.lock:
            await super()._scheduled_task(*args)  # interaction_check is checked in here
