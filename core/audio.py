from __future__ import annotations

from pathlib import Path
from typing import Tuple, List

import librosa
import numpy as np


def load_audio_from_upload(uploaded_file, outputs_dir: Path) -> Tuple[np.ndarray, int, Path]:
    """
    Save uploaded file to disk and load via librosa.
    Returns (y, sr, temp_audio_path).
    """
    outputs_dir.mkdir(exist_ok=True, parents=True)

    tmp_path = outputs_dir / f"tmp_{uploaded_file.name}"
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # librosa can decode mp3 if ffmpeg is present; packages.txt installs ffmpeg
    y, sr = librosa.load(tmp_path, sr=None, mono=True)

    return y, sr, tmp_path


def get_onset_times(y: np.ndarray, sr: int, max_events: int = 3, min_gap: float = 0.5) -> List[float]:
    """
    Detect onset times (moments sound starts). We only need a few events (A,B,C).
    Adds a small min-gap filter to avoid near-duplicate onsets common with TTS.
    """
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    onset_times = sorted(float(t) for t in onset_times if t >= 0)

    # Min-gap filter (prevents B and C almost on top of each other)
    filtered = []
    for t in onset_times:
        if not filtered or (t - filtered[-1]) >= min_gap:
            filtered.append(t)

    onset_times = filtered

    # If enough, take first N
    if len(onset_times) >= max_events:
        return onset_times[:max_events]

    # Fallback: evenly space across duration if detection is weak
    duration = len(y) / float(sr) if sr else 0
    if duration <= 0:
        return []

    if len(onset_times) == 0:
        step = duration / (max_events + 1)
        return [step * (i + 1) for i in range(max_events)]

    # Pad remaining events with reasonable spacing
    needed = max_events - len(onset_times)
    last_time = onset_times[-1]
    remaining = max(duration - last_time, 0.8)
    step = remaining / (needed + 1)
    for i in range(needed):
        onset_times.append(last_time + step * (i + 1))

    return onset_times[:max_events]

