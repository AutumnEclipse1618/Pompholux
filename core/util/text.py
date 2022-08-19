import re
from typing import Dict, Callable, Tuple

__all__ = [
    "make_translation",
    "make_escape",
]


def _trans_func(translation: Dict[str, str]) -> Callable[[str], str]:
    """
    Create function that performs transliteration according to input dictionary

    https://stackoverflow.com/a/63230728
    """
    regex = re.compile('|'.join(map(re.escape, translation)))
    return lambda text: regex.sub(lambda match: translation[match[0]], text)


def make_translation(translation: Dict[str, str]) -> Tuple[Callable[[str], str], Callable[[str], str]]:
    """
    :return: Escape function and unescape function
    """
    # noinspection PyTypeChecker
    inverse = {v: k for k, v in reversed(translation.items())}
    return _trans_func(translation), _trans_func(inverse)


def make_escape(
        chars: str = "",
        escape: str = "\\"
) -> Tuple[Callable[[str], str], Callable[[str], str], Callable[[str], str]]:
    """
    Create escape and unescape functions for specified characters

    :param chars: List of characters to escape (duplicate of escape character is automatically included)
    :param escape: Escape character to use
    :return: Escape function and unescape function
    """
    chars = escape + chars
    escape_dict: Dict[str, str] = {}
    unescape_dict: Dict[str, str] = {}
    rev_escape_dict: Dict[str, str] = {}
    for i, c in enumerate(chars.__iter__()):
        esc = chr(ord('\uE000')+i)
        escape_dict[rf'{escape}{c}'] = esc
        unescape_dict[esc] = c
        rev_escape_dict[c] = rf'{escape}{c}'
    return _trans_func(escape_dict), _trans_func(unescape_dict), _trans_func(rev_escape_dict)
