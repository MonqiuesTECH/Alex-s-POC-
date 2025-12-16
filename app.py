import sys
import uuid
from pathlib import Path

import streamlit as st

# Ensure repo root is importable
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.assets import ensure_assets
from core.audio import load_audio_from_upload, get_onset_times
from core.storyboard import build_storyboard, DEFAULT_LABELS
from core.render import render_video


BASE_DIR = ROOT
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)

st.set_page_config(page_title="Lothgha Visual-AI POC", layout="centered")


def main():
    st.title("Lothgha Visual-AI POC")
    st.write(
        "Upload a short ABC / nursery rhyme audio clip and this POC will create "
        "a simple alphabet-animals video synced to the audio."
    )

    # Ensure assets exist (creates placeholders if missing)
    assets = ensure_assets(BASE_DIR)
    bg_path = assets["bg_default"]

    audio_file = st.file_uploader(
        "Upload audio file (recommended: < 60 seconds, WAV/MP3/M4A)",
        type=["wav", "mp3", "m4a"],
    )

    st.selectbox("Visual theme", options=["Alphabet Animals (A, B, C)"], index=0)

    if st.button("Generate video"):
        if not audio_file:
            st.error("Please upload an audio file first.")
            return

        with st.spinner("Processing audio..."):
            y, sr, tmp_audio_path = load_audio_from_upload(audio_file, OUTPUTS_DIR)
            onset_times = get_onset_times(y, sr, max_events=len(DEFAULT_LABELS), min_gap=0.55)

        st.success(f"Detected {len(onset_times)} key timing points.")

        with st.spinner("Building storyboard..."):
            storyboard = build_storyboard(onset_times, DEFAULT_LABELS)

        st.subheader("Storyboard preview")
        st.json(storyboard)

        with st.spinner("Rendering video (this may take up to a minute)..."):
            output_filename = f"lothgha_demo_{uuid.uuid4().hex[:8]}.mp4"
            output_path = OUTPUTS_DIR / output_filename

            final_path = render_video(
                audio_path=str(tmp_audio_path),
                storyboard=storyboard,
                background_path=str(bg_path),
                output_path=str(output_path),
            )

        st.success("Video generated successfully!")

        video_bytes = Path(final_path).read_bytes()
        st.video(video_bytes)

        st.download_button(
            label="Download video",
            data=video_bytes,
            file_name=output_filename,
            mime="video/mp4",
        )

    st.caption("POC scope: tuned for ABC-style clips and A/B/C alphabet animals.")


if __name__ == "__main__":
    main()

