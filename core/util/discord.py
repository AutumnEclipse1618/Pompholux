from typing import List, TypeGuard

import discord


def is_str_list(val: List[object]) -> TypeGuard[List[str]]:
    """Determines whether all objects in the list are strings"""
    return all(isinstance(x, str) for x in val)


def walk_components(message: discord.Message) -> List[discord.Button | discord.SelectMenu]:
    result: List[discord.Button | discord.SelectMenu] = []

    def _walk(cs: List[discord.Component]):
        for c in cs:
            if c.type == discord.ComponentType.action_row:
                c: discord.ActionRow
                _walk(c.children)
            else:
                c: discord.Button | discord.SelectMenu
                result.append(c)

    _walk(message.components)
    return result
