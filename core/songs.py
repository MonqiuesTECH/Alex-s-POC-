from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class SongTemplate:
    key: str
    title: str
    tokens: List[str]
    # For colors template, optionally set a color swatch hex per token.
    # If provided, must match length of tokens OR be empty.
    token_colors: Optional[List[str]] = None


def _repeat_to_length(base: List[str], target_len: int) -> List[str]:
    if target_len <= 0:
        return []
    out = []
    i = 0
    while len(out) < target_len:
        out.append(base[i % len(base)])
        i += 1
    return out[:target_len]


def get_templates(target_events: int = 72) -> List[SongTemplate]:
    """
    target_events determines how many on-screen changes occur over 3 minutes.
    72 events => ~one change every 2.5 seconds (180/72).
    """

    # ABC template (A-Z repeated)
    alphabet = [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    abc_tokens = _repeat_to_length(alphabet, target_events)

    # Numbers template (1-20 repeated)
    nums = [str(n) for n in range(1, 21)]
    number_tokens = _repeat_to_length(nums, target_events)

    # Colors template (10 colors repeated)
    colors = [
        "RED", "ORANGE", "YELLOW", "GREEN", "BLUE",
        "PURPLE", "PINK", "BROWN", "BLACK", "WHITE"
    ]
    color_hex = [
        "#FF3B30", "#FF9500", "#FFCC00", "#34C759", "#007AFF",
        "#AF52DE", "#FF2D55", "#A2845E", "#111111", "#FFFFFF"
    ]
    color_tokens = _repeat_to_length(colors, target_events)
    color_swatches = _repeat_to_length(color_hex, target_events)

    return [
        SongTemplate(key="abc", title="ABC Song (3 minutes)", tokens=abc_tokens),
        SongTemplate(key="numbers", title="Numbers Song (3 minutes)", tokens=number_tokens),
        SongTemplate(key="colors", title="Colors Song (3 minutes)", tokens=color_tokens, token_colors=color_swatches),
    ]


def get_template_by_key(key: str, target_events: int = 72) -> SongTemplate:
    for t in get_templates(target_events=target_events):
        if t.key == key:
            return t
    # default
    return get_templates(target_events=target_events)[0]
