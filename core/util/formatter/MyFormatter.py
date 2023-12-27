import re
from abc import ABC, abstractmethod
from typing import Iterable, Callable

from core.util import compose, json_escape

from . import MyFormatterGrammar as Grammar


class MyFormatter:
    # Public API

    @classmethod
    def format(cls, format_string: str, recurse: Iterable[str] = (), **kwargs: str | bool) -> str:
        vals = {k.casefold(): v for k, v in kwargs.items() if isinstance(v, str)}
        conds = {
            **{k.casefold(): v for k, v in kwargs.items() if isinstance(v, bool)},
            **{k: bool(v) for k, v in vals.items()},
        }
        recurse = {s.casefold() for s in recurse}

        formatter = cls(vals, conds, recurse)
        return formatter.parse(format_string)

    @classmethod
    def escape(cls, s: str):
        return s.replace("%", "%%")

    # Inner workings

    def __init__(self, vals: dict[str, str] = None, conds: dict[str, bool] = None, recurse: set[str] = None):
        self.vals: dict[str, str] = {k.casefold(): v for k, v in vals.items()} if vals is not None else {}
        self.conds: dict[str, bool] = {k.casefold(): v for k, v in conds.items()} if conds is not None else {}
        self.recurse: set[str] = {k.casefold() for k in recurse} if recurse is not None else set()

    def parse(self, format_string):
        return Grammar.parse(format_string, actions=self.Actions, types=self.Types).evaluate(self)

    conversions: dict[str, Callable[[str], str]] = {
        "j": lambda s: json_escape(s),
        "u": lambda s: s.upper(),
        "l": lambda s: s.lower(),
    }

    @classmethod
    def convert(cls, string: str, conversion: Iterable[str]) -> str:
        return compose((cls.conversions[c.casefold()] for c in conversion), string)

    class Actions:
        @staticmethod
        def text(input, start, end, elements: list[Grammar.TreeNode | str]) -> str:
            return "".join(e if isinstance(e, str) else e.text for e in elements)

        @staticmethod
        def escape(input, start, end, elements) -> str:
            return "%"

    class Types:
        class LazyNode(ABC):
            @abstractmethod
            def evaluate(self, formatter: "MyFormatter") -> str:
                pass

        class Everything(LazyNode):
            elements: "list[MyFormatter.Types.LazyNode | str]"

            def evaluate(self, formatter: "MyFormatter") -> str:
                return "".join(e if isinstance(e, str) else e.evaluate(formatter) for e in self.elements)

        class Value(LazyNode):
            variable: Grammar.TreeNode
            conversion: Grammar.TreeNode2 | Grammar.TreeNode

            def evaluate(self, formatter: "MyFormatter") -> str:
                variable: str = self.variable.text.casefold()
                conversion: str = self.conversion.elements[0].text if len(self.conversion.elements) > 0 else ""
                return_value = formatter.vals[variable]
                return_value = formatter.parse(return_value) if variable in formatter.recurse else return_value
                return_value = formatter.convert(return_value, conversion)
                return return_value

        class Condition(LazyNode):
            negation: Grammar.TreeNode
            variable: Grammar.TreeNode
            conversion: Grammar.TreeNode4 | Grammar.TreeNode
            true_value: Grammar.TreeNode5 | Grammar.TreeNode
            false_value: Grammar.TreeNode6 | Grammar.TreeNode

            def evaluate(self, formatter: "MyFormatter") -> str:
                negation: bool = bool(self.negation.text)
                variable: str = self.variable.text.casefold()
                conversion: str = self.conversion.elements[0].text.casefold() if len(self.conversion.elements) > 0 else ""
                true_value: "MyFormatter.Types.Everything" = self.true_value.everything if len(self.true_value.elements) > 0 else None
                false_value: "MyFormatter.Types.Everything" = self.false_value.everything if len(self.false_value.elements) > 0 else None
                return_value = (true_value.evaluate(formatter) if true_value else "") if (formatter.conds[variable] if not negation else not formatter.conds[variable]) else (false_value.evaluate(formatter) if false_value else "")
                if "r" not in conversion and return_value.startswith("\n"):
                    lines = return_value.splitlines()[1:]
                    if re.fullmatch(r"[ \t]+", lines[-1]):
                        lines.pop()
                    return_value = "\n".join([l.lstrip() for l in lines])
                return return_value
