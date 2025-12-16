import sys
import uuid
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.audio import load_audio_from_upload, get_onset_times
from core.storyboard import build_storyboard, DEFAULT_LABELS
from core.render import render_video
from core.assets import ensure_default_background

BASE_DIR = ROOT
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)

# We'll generate assets dynamically into outputs/ so we don't depend on repo PNG files.
GENERATED_ASSETS_DIR = OUTPUTS_DIR / "generated_assets" / "alphabet"
BACKGROUND_PATH = OUTPUTS_DIR / "generated_assets" / "backgrounds" / "bg_default.png"

st.set_page_config(page_title="Lothgha Visual-AI POC", layout="centered")


def main():
    st.title("Lothgha Visual-AI POC")
    st.write(
        "Upload a short ABC / nursery rhyme audio clip and this POC will create "
        "a simple alphabet-animals video synced to the audio."
    )

    audio_file = st.file_uploader(
        "Upload audio file (recommended: < 60 seconds, WAV/MP3/M4A)",
        type=["wav", "mp3", "m4a"],
    )

    st.selectbox("Visual theme", options=["Alphabet Animals (A, B, C)"], index=0)

    if st.button("Generate video"):
        if not audio_file:
            st.error("Please upload an audio file first.")
            return

        # Ensure we have a background (optional but nice)
        bg_path_str = ensure_default_background(BACKGROUND_PATH, resolution=(1280, 720))

        with st.spinner("Processing audio..."):
            try:
                y, sr, tmp_audio_path = load_audio_from_upload(audio_file, OUTPUTS_DIR)
            except Exception as e:
                st.error(f"Failed to load audio: {e}")
                return

            onset_times = get_onset_times(y, sr, max_events=len(DEFAULT_LABELS))
            if not onset_times:
                st.error("Could not detect timing points from the audio. Try a clearer recording.")
                return

        st.success(f"Detected {len(onset_times)} key timing points.")

        with st.spinner("Building storyboard..."):
            storyboard = build_storyboard(onset_times, DEFAULT_LABELS, GENERATED_ASSETS_DIR)

        st.subheader("Storyboard preview")
        st.json(storyboard)

        with st.spinner("Rendering video..."):
            output_filename = f"lothgha_demo_{uuid.uuid4().hex[:8]}.mp4"
            output_path = OUTPUTS_DIR / output_filename

            try:
                final_path = render_video(
                    audio_path=str(tmp_audio_path),
                    storyboard=storyboard,
                    background_path=bg_path_str,
                    output_path=str(output_path),
                )
            except Exception as e:
                st.error(f"Failed to render video: {e}")
                return

        st.success("Video generated successfully!")

        video_bytes = Path(final_path).read_bytes()
        st.video(video_bytes)

        st.download_button(
            label="Download video",
            data=video_bytes,
            file_name=output_filename,
            mime="video/mp4",
        )

    st.caption("POC scope: short clips; A/B/C alphabet animals; simple beat/onset sync.")


if __name__ == "__main__":
    main()
