from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw

from app.config import get_settings

BASE_DIR = Path(__file__).resolve().parent.parent
PANEL_DIR = BASE_DIR / "static" / "panels"
PANEL_DIR.mkdir(parents=True, exist_ok=True)


def generate_image(prompt: str, panel_number: int):
    settings = get_settings()
    width = settings.image_width
    height = settings.image_height

    filename = f"panel_{panel_number}_{uuid4().hex}.png"
    file_path = PANEL_DIR / filename

    image = Image.new("RGB", (width, height), color=(18, 24, 38))
    draw = ImageDraw.Draw(image)

    # Simple abstract comic-panel art for demo mode.
    for y in range(0, height, 24):
        color = (40 + (y % 80), 60 + (y % 70), 90 + (y % 90))
        draw.rectangle((0, y, width, y + 20), fill=color)

    draw.rectangle((40, 40, width - 40, height - 40), outline=(255, 255, 255), width=3)
    draw.rounded_rectangle((80, 80, width - 80, height - 120), radius=20, outline=(255, 196, 87), width=4)

    text = f"Panel {panel_number}"
    draw.text((100, 100), text, fill=(255, 255, 255))

    wrap = prompt[:180]
    draw.text((100, height - 150), wrap, fill=(224, 236, 255))

    image.save(file_path)
    return f"/static/panels/{filename}"
