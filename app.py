import sys
import uuid
from pathlib import Path

import streamlit as st

# --- Make sure we can import from the repo root -----------------------------

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.audio import load_audio_from_upload, get_onset_times
from core.storyboard import build_storyboard, DEFAULT_LABELS
from core.render import render_video

# --- Paths ------------------------------------------------------------------

BASE_DIR = ROOT
ASSETS_DIR = BASE_DIR / "assets"
OUTPUTS_DIR = BASE_DIR / "outputs"
BACKGROUND_PATH = ASSETS_DIR / "backgrounds" / "bg_default.png"

OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)

# --- Streamlit config -------------------------------------------------------

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

    theme = st.selectbox(
        "Visual theme",
        options=["Alphabet Animals (A, B, C)"],
        index=0,
    )

    generate_btn = st.button("Generate video")

    if generate_btn:
        if not audio_file:
            st.error("Please upload an audio file first.")
            return

        # --- Audio processing ------------------------------------------------
        with st.spinner("Processing audio..."):
            try:
                y, sr, tmp_audio_path = load_audio_from_upload(audio_file, OUTPUTS_DIR)
            except Exception as e:
                st.error(f"Failed to load audio: {e}")
                return

            onset_times = get_onset_times(y, sr, max_events=len(DEFAULT_LABELS))

            if not onset_times:
                st.error(
                    "Could not detect any clear onsets in the audio. "
                    "Try a clearer or louder recording, or a shorter clip."
                )
                return

        st.success(f"Detected {len(onset_times)} key timing points.")

        # --- Storyboard ------------------------------------------------------
        with st.spinner("Building storyboard..."):
            storyboard = build_storyboard(onset_times, DEFAULT_LABELS)

        if not storyboard:
            st.error("Storyboard is empty. Check your audio and assets mapping.")
            return

        st.subheader("Storyboard preview")
        st.json(storyboard)

        if not BACKGROUND_PATH.exists():
            st.warning(
                f"Background image not found at {BACKGROUND_PATH}. "
                "A solid-color background will be used instead (handled in render)."
            )

        # --- Video rendering -------------------------------------------------
        with st.spinner("Rendering video (this may take up to a minute)..."):
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
                return

        st.success("Video generated successfully!")

        # --- Display + download ---------------------------------------------
        try:
            with open(final_path, "rb") as f:
                video_bytes = f.read()
        except Exception as e:
            st.error(f"Video file was created but could not be read: {e}")
            return

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


if __name__ == "__main__":
    main()
