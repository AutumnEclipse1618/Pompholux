import json
from typing import TypeGuard, TypedDict, Any

import discord
import jsonschema

from core.util import MyJSONValidation, MyJSONValidationError


def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
    """Determines whether all objects in the list are strings"""
    return all(isinstance(x, str) for x in val)


def walk_components(message: discord.Message) -> list[discord.Button | discord.SelectMenu]:
    result: list[discord.Button | discord.SelectMenu] = []

    def _walk(cs: list[discord.Component]):
        for c in cs:
            if c.type == discord.ComponentType.action_row:
                c: discord.ActionRow
                _walk(c.children)
            else:
                c: discord.Button | discord.SelectMenu
                result.append(c)

    _walk(message.components)
    return result


class ContentResult(TypedDict):
    content: str
    embeds: list[discord.Embed]


class ContentValidation(MyJSONValidation):
    content_validator = jsonschema.Draft202012Validator({
        "type": "object",
        "minProperties": 1,
        "additionalProperties": False,
        "properties": {
            "content": {"type": "string", "minLength": 1},
            "embed": {"$anchor": "embed", "type": "object", "minProperties": 1},
            "embeds": {"type": "array", "minItems": 1, "maxItems": 10, "items": {"$ref": "#embed"}},
        },
        "not": {"$anchor": "notEmbeds", "required": ["embed", "embeds"]},  # Not have both "embed" and "embeds"
    })

    def __init__(self):
        super().__init__(self.content_validator)  # noqa

    def parse(self, string: str) -> ContentResult:
        if not string.startswith("{"):
            return ContentResult(content=string, embeds=[])
        else:
            try:
                dct: dict[str, Any] = super().parse(string)
            except Exception as ex:
                match ex:
                    case Exception(__cause__=jsonschema.ValidationError(
                        json_path=json_path, validator="not", validator_value={"$anchor": "notEmbeds"}
                    )):
                        raise MyJSONValidationError(path=json_path,
                                                    message="Cannot have both \"embed\" and \"embeds\" properties"
                                                    ) from ex.__cause__
                    case _:
                        raise ex
            if "embed" in dct:
                dct["embeds"] = [dct["embed"]]
            return ContentResult(
                content=dct["content"] if "content" in dct else "",
                embeds=[discord.Embed.from_dict(e) for e in dct["embeds"]] if "embeds" in dct else []
            )
