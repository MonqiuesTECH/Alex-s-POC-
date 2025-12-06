# Lothgha Visual-AI POC

This is a minimal proof-of-concept for generating simple, kid-friendly videos
from short ABC / nursery rhyme audio clips.

The app:

1. Lets you upload a short audio file (e.g., someone singing "A, B, C").
2. Detects a few key timing points in the audio.
3. Maps those times to pre-made alphabet animal images (A = alligator, B = bear, C = cat).
4. Renders a 720p MP4 video with the images appearing roughly in sync with the audio.

## Tech Stack

- Streamlit (UI)
- Python (3.10+ recommended)
- librosa (audio analysis)
- MoviePy (video composition)
- Pillow (image handling)

## Project Structure

```bash
lothgha-visual-ai-poc/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── core/
│   ├── __init__.py
│   ├── audio.py
│   ├── storyboard.py
│   └── render.py
├── assets/
│   ├── alphabet/
│   │   ├── A_alligator.png
│   │   ├── B_bear.png
│   │   └── C_cat.png
│   ├── icons/
│   │   └── star.png
│   └── backgrounds/
│       └── bg_default.png
├── sample_audio/
│   └── abc_demo.wav   # (optional)
└── outputs/
    └── (generated videos)
