import json
from typing import TypeGuard, TypedDict, Any

import discord
import jsonschema

from bot.error import UserInputWarning


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


# TODO make validation extensible
# TODO replace VALIDATION_ERR_MSG {field}
class ContentValidation:
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
    VALIDATOR_ERR_MSG = \
        ":x: \"{field}\" JSON does not conform to schema\n" \
        "```\nError at element {path}\n" \
        "{message}```"

    @classmethod
    def validation_error(cls, *args, **kwargs):
        return UserInputWarning(cls.VALIDATOR_ERR_MSG.format(*args, **kwargs))

    @classmethod
    def parse(cls, content: str) -> ContentResult:
        if not content.startswith("{"):
            return ContentResult(content=content, embeds=[])
        else:
            try:
                dct: dict[str, Any] = json.loads(content)
                cls.content_validator.validate(dct)
            except Exception as ex:
                match ex:
                    case json.JSONDecodeError():
                        raise UserInputWarning(f":x: \"Content\" input is not valid JSON\n```\n{ex}```") from ex
                    case jsonschema.ValidationError(
                        json_path=json_path, validator="maxItems" | "maxLength", validator_value=_max
                    ):
                        raise cls.validation_error(field="Content", path=json_path,
                                                   message=f"Maximum length is {_max}") from ex
                    case jsonschema.ValidationError(
                        json_path=json_path, validator="minProperties" | "minItems" | "minLength", validator_value=_min
                    ) if _min == 1:
                        raise cls.validation_error(field="Content", path=json_path,
                                                   message="Value cannot be empty") from ex
                    case jsonschema.ValidationError(
                        json_path=json_path, validator="not", validator_value={"$anchor": "notEmbeds"}
                    ):
                        raise cls.validation_error(field="Content", path=json_path,
                                                   message="Cannot have both \"embed\" and \"embeds\" properties"
                                                   ) from ex
                    case jsonschema.ValidationError(json_path=json_path, message=message):
                        raise cls.validation_error(field="Content", path=json_path, message=message) from ex
                    case _:
                        raise ex
            if "embed" in dct:
                dct["embeds"] = [dct["embed"]]
            return ContentResult(
                content=dct["content"] if "content" in dct else "",
                embeds=[discord.Embed.from_dict(e) for e in dct["embeds"]] if "embeds" in dct else []
            )
