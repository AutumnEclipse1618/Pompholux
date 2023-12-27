import enum
import itertools
import json
import re
from typing import Callable, TypeAlias, Any, Iterable

import jsonschema

from bot.error import UserInputWarning

__all__ = [
    "convert_to_bool",
    "make_translation",
    "make_escape",
    "json_escape",
    "MyJSONValidation",
    "MyJSONValidationError",
]

from core.util import compose


def convert_to_bool(argument: str) -> bool | None:
    """
    Convert string to bool, based on discord.py's logic

    https://github.com/Rapptz/discord.py/blob/v2.0.0/discord/ext/commands/converter.py#L1142
    """
    lowered = argument.lower()
    if lowered in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
        return True
    elif lowered in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
        return False
    else:
        return False


def _trans_func(translation: dict[str, str]) -> Callable[[str], str]:
    """
    Create function that performs transliteration according to input dictionary

    https://stackoverflow.com/a/63230728
    """
    regex = re.compile('|'.join(map(re.escape, translation)))
    return lambda text: regex.sub(lambda match: translation[match[0]], text)


def make_translation(translation: dict[str, str]) -> tuple[Callable[[str], str], Callable[[str], str]]:
    """
    :return: Escape function and unescape function
    """
    # noinspection PyTypeChecker
    inverse = {v: k for k, v in reversed(translation.items())}
    return _trans_func(translation), _trans_func(inverse)


Escape: TypeAlias = tuple[Callable[[str], str], Callable[[str], str], Callable[[str], str]]


def make_escape(escape: str | list[str] = "\\", chars: str | list[str] = "") -> Escape:
    """
    Create escape and unescape functions for specified characters

    :param escape: Escape character to use or list of multiple escape characters
    :param chars: String listing characters to escape (duplicate of escape character is automatically included), or a list of strings that are zipped with the list of escape characters
    :return: Escape function and unescape function
    """
    if isinstance(escape, str):
        escape = [escape]
    if isinstance(chars, str):
        chars = itertools.repeat(chars, len(escape))
    escape_dict: dict[str, str] = {}
    unescape_dict: dict[str, str] = {}
    rev_escape_dict: dict[str, str] = {}
    for i, (e, c) in enumerate((e, e + c) for e, c in zip(escape, chars, strict=True)):
        esc = chr(ord('\uE000')+i)
        escape_dict[rf'{e}{c}'] = esc
        unescape_dict[esc] = c
        rev_escape_dict[c] = rf'{e}{c}'
    return _trans_func(escape_dict), _trans_func(unescape_dict), _trans_func(rev_escape_dict)


def json_escape(string: str) -> str:
    return json.dumps(string)[1:-1]


class MyJSONValidationError(Exception):
    DECODER_ERR_MSG = \
        ":x: \"{field}\" input is not valid JSON\n" \
        "```\n{message}```"
    VALIDATOR_ERR_MSG = \
        ":x: \"{field}\" JSON does not conform to schema\n" \
        "```\nError at element {path}\n" \
        "{message}```"

    def __init__(self, message: str, path: str | None):
        self.message = message
        self.path = path

    def user_warning(self, field: str):
        ex = UserInputWarning(
            self.VALIDATOR_ERR_MSG.format(field=field, path=self.path, message=self.message)
            if self.path
            else self.DECODER_ERR_MSG.format(field=field, message=self.message)
        )
        ex.__cause__ = self
        return ex


class MyJSONValidation:
    def __init__(self, validator: jsonschema.protocols.Validator):
        self.validator = validator

    def parse(self, string: str) -> Any:
        try:
            dct = json.loads(string)
            self.validator.validate(dct)
            return dct
        except Exception as ex:
            match ex:
                case json.JSONDecodeError():
                    raise MyJSONValidationError(path=None, message=str(ex)) from ex
                case jsonschema.ValidationError(
                    json_path=json_path, validator="maxItems" | "maxLength", validator_value=_max
                ):
                    raise MyJSONValidationError(path=json_path,
                                                message=f"Maximum length is {_max}") from ex
                case jsonschema.ValidationError(
                    json_path=json_path, validator="minProperties" | "minItems" | "minLength", validator_value=_min
                ) if _min == 1:
                    raise MyJSONValidationError(path=json_path,
                                                message="Value cannot be empty") from ex
                case jsonschema.ValidationError(json_path=json_path, message=message):
                    raise MyJSONValidationError(path=json_path, message=message) from ex
                case _:
                    raise ex
