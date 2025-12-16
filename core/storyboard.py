from __future__ import annotations

from typing import List, Dict
from pathlib import Path

from core.assets import ensure_alphabet_assets


DEFAULT_LABELS = ["A", "B", "C"]


def build_storyboard(
    onset_times: List[float],
    labels: List[str],
    generated_assets_dir: Path,
) -> List[Dict]:
    """
    Build storyboard mapping each onset time to a generated visual asset.
    """
    asset_map = ensure_alphabet_assets(generated_assets_dir)

    events: List[Dict] = []
    count = min(len(onset_times), len(labels))

    for i in range(count):
        label = labels[i]
        t = float(onset_times[i])

        asset_path = asset_map.get(label)
        if not asset_path:
            continue

        events.append(
            {
                "t": t,
                "label": label,
                "asset": asset_path,   # absolute path
                "duration": 1.2,
                "effect": "bounce",
            }
        )

    return events
