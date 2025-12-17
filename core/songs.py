from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from core.prompt_parser import parse_prompt_lines

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"


@dataclass(frozen=True)
class SongTemplate:
    key: str
    title: str
    tokens: List[str]
    token_colors: Optional[List[str]] = None


def _repeat_to_length(base: List[str], target_len: int) -> List[str]:
    if not base or target_len <= 0:
        return []
    out = []
    i = 0
    while len(out) < target_len:
        out.append(base[i % len(base)])
        i += 1
    return out[:target_len]


def _load_prompt_lines(filename: str) -> List[str]:
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing prompt file: {path}")
    return [l.strip() for l in path.read_text().splitlines() if l.strip()]


def get_templates(target_events: int = 72) -> List[SongTemplate]:
    # ---------- ABC ----------
    abc_lines = _load_prompt_lines("abc_song.txt")
    abc_units = parse_prompt_lines(abc_lines)
    abc_tokens = _repeat_to_length([u["text"] for u in abc_units], target_events)

    # ---------- NUMBERS ----------
    num_lines = _load_prompt_lines("numbers_song.txt")
    num_units = parse_prompt_lines(num_lines)
    num_tokens = _repeat_to_length([u["text"] for u in num_units], target_events)

    # ---------- COLORS ----------
    color_lines = _load_prompt_lines("colors_song.txt")
    color_units = parse_prompt_lines(color_lines)
    color_tokens = _repeat_to_length([u["text"] for u in color_units], target_events)

    COLOR_HEX = {
        "RED": "#FF3B30",
        "BLUE": "#007AFF",
        "GREEN": "#34C759",
        "YELLOW": "#FFCC00",
        "ORANGE": "#FF9500",
        "PURPLE": "#AF52DE",
        "PINK": "#FF2D55",
        "BLACK": "#111111",
        "WHITE": "#FFFFFF",
    }

    color_swatches = _repeat_to_length(
        [COLOR_HEX.get(u["text"], "#000000") for u in color_units],
        target_events,
    )

    return [
        SongTemplate(
            key="abc",
            title="ABC Song (Prompt-Based)",
            tokens=abc_tokens,
        ),
        SongTemplate(
            key="numbers",
            title="Numbers Song (Prompt-Based)",
            tokens=num_tokens,
        ),
        SongTemplate(
            key="colors",
            title="Colors Song (Prompt-Based)",
            tokens=color_tokens,
            token_colors=color_swatches,
        ),
    ]


def get_template_by_key(key: str, target_events: int = 72) -> SongTemplate:
    for t in get_templates(target_events):
        if t.key == key:
            return t
    return get_templates(target_events)[0]
