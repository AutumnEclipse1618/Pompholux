from abc import ABC
from typing import Generic, Type, TypeVar


ComponentT = TypeVar("ComponentT", bound="ComponentABC")


class AppABC(ABC):
    def create_component(self, component_cls: Type[ComponentT]) -> ComponentT:
        return component_cls(self)


AppT = TypeVar("AppT", bound=AppABC)


class ComponentABC(Generic[AppT], ABC):
    app: AppT

    def __init__(self, app: AppT):
        self.app = app
