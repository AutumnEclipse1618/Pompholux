import enum
import itertools
import re
from typing import Callable, TypeAlias

__all__ = [
    "make_translation",
    "make_escape",
    "MyFormatter",
]


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


class MyFormatter:
    # TODO strict mode

    @classmethod
    def escape(cls, string: str):
        return string.replace("$", "$$").replace("%", "%%")

    @classmethod
    def format(cls, string: str, **kwargs: str | bool) -> str:
        vals = {k: v for k, v in kwargs.items() if isinstance(v, str)}
        conds = {
            **{k: v for k, v in kwargs.items() if isinstance(v, bool)},
            **{k: bool(v) for k, v in vals.items()}
        }
        return cls._format(string, vals, conds)

    @classmethod
    def _format(cls, string: str, vals: dict[str, str], conds: dict[str, bool]) -> str:
        result = ""
        buffer = ""
        brace_level = 0

        class States(enum.Enum):
            NORMAL = enum.auto(),
            ESCAPING = enum.auto(),
            COND = enum.auto(),
            COND_AND_ESCAPING = enum.auto(),
            VAL = enum.auto(),

        state = States.NORMAL
        c: str
        prev_char: str
        for prev_char, c in itertools.pairwise(itertools.chain((SOF := 0,), string, (EOF := None,))):
            match state:
                case States.NORMAL:
                    if c is EOF:
                        continue
                    elif c == "%" or c == "$":
                        state = States.ESCAPING; continue
                    else:
                        result += c
                case States.ESCAPING:
                    if c is EOF:
                        result += prev_char
                        continue
                    elif prev_char == "%" and c == "%":
                        result += "%"
                        state = States.NORMAL; continue
                    elif prev_char == "$" and c == "$":
                        result += "$"
                        state = States.NORMAL; continue
                    elif prev_char == "%" and c == "{":
                        buffer += prev_char + c
                        brace_level += 1
                        state = States.COND; continue
                    elif prev_char == "$" and c == "{":
                        buffer += prev_char + c
                        state = States.VAL; continue
                    result += prev_char + c
                    state = States.NORMAL; continue
                case States.VAL:
                    if c is EOF:
                        result += buffer
                        continue
                    elif c == "}":
                        buffer += c
                        result += cls._format_val(buffer, vals, conds)
                        buffer = ""
                        state = States.NORMAL; continue
                    elif not re.fullmatch(r"\w", c, re.ASCII):
                        result += cls._format_val(buffer, vals, conds) + c
                        buffer = ""
                        state = States.NORMAL; continue
                    else:
                        buffer += c
                case States.COND:
                    if c is EOF:
                        result += buffer
                        continue
                    elif c == "%":
                        state = States.COND_AND_ESCAPING; continue
                    buffer += c
                case States.COND_AND_ESCAPING:
                    if c is EOF:
                        result += buffer + prev_char
                        continue
                    elif prev_char == "%" and c == "%":
                        buffer += "%"
                        state = States.COND; continue
                    elif prev_char == "%" and c == "{":
                        buffer += prev_char + c
                        brace_level += 1
                        state = States.COND; continue
                    elif prev_char == "%" and c == "}":
                        buffer += prev_char + c
                        brace_level = max(0, brace_level - 1)
                        if brace_level == 0:
                            result += cls._format_cond(buffer, vals, conds)
                            buffer = ""
                            state = States.NORMAL; continue
                        else:
                            state = States.COND; continue
                    buffer += prev_char + c
                    state = States.COND; continue
        return result

    @classmethod
    def _format_val(cls, string: str, vals: dict[str, str], conds: dict[str, bool]) -> str:
        val_regex = re.compile(r"\$\{(?P<key>\w+)\}", re.ASCII)
        val = ""
        return \
            cls._format(val, vals, conds) \
            if (match_ := val_regex.fullmatch(string)) and (val := vals.get(match_["key"].lower())) \
            else string

    @classmethod
    def _format_cond(cls, string: str, vals: dict[str, str], conds: dict[str, bool]) -> str:
        cond_regex = re.compile(r"\%\{(?P<cond>\w+)\%\|(?P<body>.*)\%\}", re.ASCII | re.DOTALL)
        if not (match := cond_regex.fullmatch(string)):
            return string
        cond = conds.get(match["cond"].lower())
        if cond is None:
            return string
        body = match["body"]

        true_val = ""
        false_val = ""
        brace_level = 0

        class States(enum.Enum):
            PARSING_TRUE = enum.auto(),
            ESCAPING_TRUE = enum.auto(),
            PARSING_FALSE = enum.auto(),

        state = States.PARSING_TRUE
        c: str
        prev_char: str
        for prev_char, c in itertools.pairwise(itertools.chain((SOF := 0,), body, (EOF := None,))):
            match state:
                case States.PARSING_TRUE:
                    if c is EOF:
                        continue
                    elif c == "%":
                        state = States.ESCAPING_TRUE; continue
                    true_val += c
                case States.ESCAPING_TRUE:
                    if c is EOF:
                        true_val += prev_char
                        continue
                    elif prev_char == "%" and c == "{":
                        brace_level += 1
                    elif prev_char == "%" and c == "}":
                        brace_level = max(0, brace_level - 1)
                    elif prev_char == "%" and c == "|":
                        if brace_level == 0:
                            state = States.PARSING_FALSE; continue
                    true_val += prev_char + c
                    state = States.PARSING_TRUE; continue
                case States.PARSING_FALSE:
                    if c is EOF:
                        continue
                    false_val += c

        return cls._format(true_val if cond else false_val, vals, conds)
