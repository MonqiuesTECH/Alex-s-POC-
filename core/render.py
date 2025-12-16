from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict

import imageio_ffmpeg
from moviepy.config import change_settings
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, ColorClip
from PIL import Image


# Force MoviePy to use the ffmpeg binary bundled by imageio-ffmpeg (reliable on Streamlit Cloud)
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
change_settings({"FFMPEG_BINARY": FFMPEG_EXE})
os.environ["IMAGEIO_FFMPEG_EXE"] = FFMPEG_EXE


def render_video(
    audio_path: str,
    storyboard: List[Dict],
    background_path: str,
    output_path: str,
    resolution=(1280, 720),
    fps: int = 30,
) -> str:
    """
    Render MP4 from audio + storyboard + background.
    """
    output_path = str(output_path)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    audio_clip = AudioFileClip(audio_path)
    audio_duration = float(audio_clip.duration)

    if storyboard:
        last_event = max(e["t"] + float(e.get("duration", 1.0)) for e in storyboard)
        total_duration = max(audio_duration, last_event + 0.5)
    else:
        total_duration = audio_duration

    bg_clip = _make_background_clip(background_path, duration=total_duration, resolution=resolution)

    w, h = resolution
    clips = [bg_clip]

    for event in storyboard:
        asset = event["asset"]
        start_t = float(event["t"])
        duration = float(event.get("duration", 1.0))

        if not Path(asset).exists():
            # If asset is missing, skip gracefully (assets.py should prevent this)
            continue

        img_clip = (
            ImageClip(asset)
            .set_start(start_t)
            .set_duration(duration)
            .resize(width=int(w * 0.55))
            .set_position("center")
            .fadein(0.15)
        )

        clips.append(img_clip)

    video = CompositeVideoClip(clips, size=resolution).set_duration(total_duration)
    video = video.set_audio(audio_clip)

    video.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=2,
        verbose=False,
        logger=None,
    )

    audio_clip.close()
    video.close()
    return output_path


def _make_background_clip(background_path: str, duration: float, resolution):
    w, h = resolution
    try:
        Image.open(background_path)  # validate file exists/opens
        return ImageClip(background_path).set_duration(duration).resize(newsize=resolution)
    except Exception:
        return ColorClip(size=(w, h), color=(245, 245, 245)).set_duration(duration)
