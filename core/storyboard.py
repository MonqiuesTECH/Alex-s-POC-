from typing import List, Dict

# For the POC we hard-code A, B, C
DEFAULT_LABELS = ["A", "B", "C"]

ASSET_MAP = {
    "A": "assets/alphabet/A_alligator.png",
    "B": "assets/alphabet/B_bear.png",
    "C": "assets/alphabet/C_cat.png",
}


def build_storyboard(onset_times: List[float], labels: List[str]) -> List[Dict]:
    """
    Build a simple storyboard mapping each onset time to a visual asset.
    Assumes len(onset_times) >= len(labels) or will only use min length.
    """
    events = []

    count = min(len(onset_times), len(labels))
    for i in range(count):
        label = labels[i]
        t = float(onset_times[i])
        asset_path = ASSET_MAP.get(label)

        if not asset_path:
            # Skip unknown labels for now
            continue

        events.append(
            {
                "t": t,
                "label": label,
                "asset": asset_path,
                "duration": 1.2,  # seconds on screen
                "effect": "bounce",  # placeholder for future use
            }
        )

    return events
