from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from PIL import Image, ImageDraw, ImageFont


ALPHABET_ANIMALS: Dict[str, str] = {
    "A": "Alligator",
    "B": "Bear",
    "C": "Cat",
}


def ensure_alphabet_assets(assets_dir: Path) -> Dict[str, str]:
    """
    Ensures A/B/C placeholder PNGs exist. Returns a mapping of label->absolute filepath.
    Generates simple kid-safe images (letter + animal word) so we don't depend on repo PNGs.
    """
    assets_dir.mkdir(parents=True, exist_ok=True)

    out: Dict[str, str] = {}
    for letter, animal in ALPHABET_ANIMALS.items():
        filename = f"{letter}_{animal.lower()}.png"
        path = assets_dir / filename
        if not path.exists():
            _generate_placeholder_letter_animal_image(letter, animal, path)
        out[letter] = str(path.resolve())

    return out


def _generate_placeholder_letter_animal_image(letter: str, animal: str, out_path: Path) -> None:
    # 1024x1024 square image, high-contrast, kid-friendly
    size = (1024, 1024)
    img = Image.new("RGBA", size, (245, 245, 245, 255))
    d = ImageDraw.Draw(img)

    # Border
    d.rounded_rectangle([30, 30, size[0] - 30, size[1] - 30], radius=60, outline=(20, 20, 20, 255), width=10)

    # Try to load a default font (works on Streamlit Cloud). If not, use PIL built-in.
    try:
        big_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 520)
        small_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 90)
    except Exception:
        big_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Big letter
    letter_bbox = d.textbbox((0, 0), letter, font=big_font)
    lw = letter_bbox[2] - letter_bbox[0]
    lh = letter_bbox[3] - letter_bbox[1]
    letter_pos = ((size[0] - lw) // 2, 170)

    # Slight “shadow” for pop
    d.text((letter_pos[0] + 10, letter_pos[1] + 10), letter, font=big_font, fill=(0, 0, 0, 80))
    d.text(letter_pos, letter, font=big_font, fill=(15, 60, 170, 255))

    # Animal label
    text = f"{animal}"
    t_bbox = d.textbbox((0, 0), text, font=small_font)
    tw = t_bbox[2] - t_bbox[0]
    th = t_bbox[3] - t_bbox[1]
    t_pos = ((size[0] - tw) // 2, 760)

    # Highlight pill behind animal
    pill = [t_pos[0] - 40, t_pos[1] - 20, t_pos[0] + tw + 40, t_pos[1] + th + 20]
    d.rounded_rectangle(pill, radius=40, fill=(255, 230, 120, 255), outline=(20, 20, 20, 255), width=6)

    d.text(t_pos, text, font=small_font, fill=(20, 20, 20, 255))

    img.save(out_path, "PNG")


def ensure_default_background(bg_path: Path, resolution: Tuple[int, int] = (1280, 720)) -> str:
    """
    Optional: create a background PNG if you want a consistent look.
    If it exists already, does nothing.
    """
    bg_path.parent.mkdir(parents=True, exist_ok=True)

    if not bg_path.exists():
        w, h = resolution
        img = Image.new("RGB", (w, h), (230, 245, 255))
        d = ImageDraw.Draw(img)

        # Simple soft stripes
        for i in range(0, w, 80):
            d.rectangle([i, 0, i + 40, h], fill=(220, 240, 255))

        img.save(bg_path, "PNG")

    return str(bg_path.resolve())
