import asyncio
from abc import ABC, abstractmethod
from typing import Optional, List, Type, TypeVar, Callable, Any

import discord

RawViewT = TypeVar("RawViewT", bound="RawView")
FuncT = TypeVar('FuncT', bound=Callable[..., Any])


class RawViewStore:
    def __init__(self):
        self.raw_views: List[Type[RawViewT]] = []

    def add_raw_view(self, view: Type[RawViewT]):
        if view in self.raw_views:
            raise ValueError("Raw view already registered")
        self.raw_views.append(view)

    def remove_raw_view(self, view: Type[RawViewT]) -> bool:
        try:
            self.raw_views.remove(view)
        except ValueError:
            return False
        return True

    def dispatch_raw_view(
            self,
            component_type: discord.enums.ComponentType,
            custom_id: str,
            interaction: discord.Interaction
    ):
        view: Type[RawViewT] = discord.utils.find(
            lambda v: v.interaction_filter(component_type, custom_id),
            self.raw_views
        )
        if view is not None:
            asyncio.create_task(
                self.scheduled_raw_view_task(view, component_type, custom_id, interaction),
                name=f'my-raw_view-dispatch-{view.__name__}'
            )

    async def scheduled_raw_view_task(
            self,
            view: Type[RawViewT],
            component_type: discord.enums.ComponentType,
            custom_id: str,
            interaction: discord.Interaction
    ):
        try:
            allow = await view.raw_interaction_check(component_type, custom_id, interaction)
            if not allow:
                return
            await view.dispatch(component_type, custom_id, interaction)
        except Exception as error:
            await self.dispatch_raw_error(view, component_type, custom_id, interaction, error)

    async def dispatch_raw_error(
            self,
            view: Type[RawViewT],
            component_type: discord.enums.ComponentType,
            custom_id: str,
            interaction: discord.Interaction,
            error: Exception
    ):
        raw_view_handler = view.on_raw_error if view.has_raw_error_handler() else None
        ex = error
        if raw_view_handler is not None:
            try:
                await raw_view_handler(component_type, custom_id, interaction, ex)
            except Exception as ex_raw_view:
                ex = ex_raw_view
            else:
                return
        interaction.client.dispatch("raw_view_error", view, component_type, custom_id, interaction, ex)


def _raw_view_special_method(func: FuncT) -> FuncT:
    func.__raw_view_special_method__ = None
    return func


class RawView(discord.ui.View, ABC):
    def __init__(self, *, timeout: Optional[float] = None):
        super().__init__(timeout=timeout)

    @classmethod
    @abstractmethod
    def interaction_filter(cls, component_type: discord.enums.ComponentType, custom_id: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    async def dispatch(
            cls,
            component_type: discord.enums.ComponentType,
            custom_id: str,
            interaction: discord.Interaction
    ):
        pass

    # noinspection PyUnusedLocal
    @classmethod
    async def raw_interaction_check(
            cls,
            component_type: discord.enums.ComponentType,
            custom_id: str,
            interaction: discord.Interaction
    ):
        return True

    @classmethod
    def has_raw_error_handler(cls) -> bool:
        """:class:`bool`: Checks whether the raw view has an error handler."""
        return not hasattr(cls.on_raw_error.__func__, '__raw_view_special_method__')

    # noinspection PyUnusedLocal
    @classmethod
    @_raw_view_special_method
    async def on_raw_error(
            cls,
            component_type: discord.enums.ComponentType,
            custom_id: str,
            interaction: discord.Interaction,
            error: Exception
    ) -> None:
        pass
