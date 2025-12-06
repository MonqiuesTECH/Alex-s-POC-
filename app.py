import os
import uuid
from pathlib import Path

import streamlit as st

from core.audio import load_audio_from_upload, get_onset_times
from core.storyboard import build_storyboard, DEFAULT_LABELS
from core.render import render_video

# Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUTS_DIR = BASE_DIR / "outputs"
BACKGROUND_PATH = ASSETS_DIR / "backgrounds" / "bg_default.png"

OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)


st.set_page_config(page_title="Lothgha Visual-AI POC", layout="centered")

st.title("Lothgha Visual-AI POC")
st.write(
    "Upload a short ABC / nursery rhyme audio clip and this POC will create "
    "a simple alphabet-animals video synced to the audio."
)

audio_file = st.file_uploader(
    "Upload audio file (recommended: < 60 seconds, WAV/MP3/M4A)",
    type=["wav", "mp3", "m4a"],
)

theme = st.selectbox(
    "Visual theme",
    options=["Alphabet Animals (A, B, C)"],
    index=0,
)

generate_btn = st.button("Generate video")

if generate_btn:
    if not audio_file:
        st.error("Please upload an audio file first.")
        st.stop()

    with st.spinner("Processing audio..."):
        try:
            y, sr, tmp_audio_path = load_audio_from_upload(audio_file, OUTPUTS_DIR)
        except Exception as e:
            st.error(f"Failed to load audio: {e}")
            st.stop()

        onset_times = get_onset_times(y, sr, max_events=len(DEFAULT_LABELS))

        if not onset_times:
            st.error("Could not detect any clear onsets in the audio. "
                     "Try a clearer or louder recording.")
            st.stop()

    st.success(f"Detected {len(onset_times)} key timing points.")

    with st.spinner("Building storyboard..."):
        storyboard = build_storyboard(onset_times, DEFAULT_LABELS)

    st.write("Storyboard preview (time → asset):")
    st.json(storyboard)

    with st.spinner("Rendering video (this may take a bit)..."):
        output_filename = f"lothgha_demo_{uuid.uuid4().hex[:8]}.mp4"
        output_path = OUTPUTS_DIR / output_filename

        try:
            final_path = render_video(
                audio_path=str(tmp_audio_path),
                storyboard=storyboard,
                background_path=str(BACKGROUND_PATH),
                output_path=str(output_path),
            )
        except Exception as e:
            st.error(f"Failed to render video: {e}")
            st.stop()

    st.success("Video generated successfully!")

    with open(final_path, "rb") as f:
        video_bytes = f.read()

    st.video(video_bytes)

    st.download_button(
        label="Download video",
        data=video_bytes,
        file_name=output_filename,
        mime="video/mp4",
    )

st.caption(
    "POC scope: tuned for short ABC / nursery-rhyme style clips and A/B/C alphabet animals."
)
