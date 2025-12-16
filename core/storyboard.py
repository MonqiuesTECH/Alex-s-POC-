from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from core.visuals import ensure_visual_assets

DEFAULT_LABELS = ["A", "B", "C"]


def build_storyboard(onset_times: List[float], labels: List[str], assets_dir: Path) -> List[Dict]:
    assets = ensure_visual_assets(assets_dir)

    n = min(len(onset_times), len(labels))
    events: List[Dict] = []
    for i in range(n):
        label = labels[i]
        if label not in assets:
            continue
        events.append(
            {
                "t": float(onset_times[i]),
                "label": label,
                "asset": assets[label],  # absolute path
                "duration": 1.2,
                "effect": "pop",
            }
        )
    return events
