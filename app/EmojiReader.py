import itertools
import json
from typing import Dict

__all__ = ["read_emoji"]


def read_emoji(file: str) -> Dict[str, str]:
    with open(file, "r", encoding="utf-8") as f:
        emoji_raw = json.load(f)
    emoji_list = [
        e
        for emoji_category in emoji_raw.values()
        for e in emoji_category
    ]
    emoji_list_diversity = [
        e
        for emoji in emoji_list if emoji.get("hasDiversity", False)
        for e in emoji["diversityChildren"]
    ]
    emojis = {
        n: e["surrogates"]
        for e in itertools.chain(emoji_list, emoji_list_diversity)
        for n in e["names"]
    }
    return emojis
