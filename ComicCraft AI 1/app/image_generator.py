from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
PANEL_DIR = BASE_DIR / "static" / "panels"
PANEL_DIR.mkdir(parents=True, exist_ok=True)


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def generate_image(prompt: str, panel_number: int) -> str:
    """Create a demo panel image for the comic preview."""
    filename = f"panel_{panel_number}.png"
    path = PANEL_DIR / filename

    image = Image.new("RGB", (1200, 900), color=(30, 41, 59))
    draw = ImageDraw.Draw(image)

    for i in range(0, 300, 30):
        color = (i % 180 + 50, 80 + (i % 120), 150 + (i % 80))
        draw.rectangle((0, i, 1200, i + 20), fill=color)

    draw.rounded_rectangle((80, 80, 1120, 820), radius=24, outline=(255, 255, 255), width=4)
    draw.text((100, 120), f"Panel {panel_number}", fill=(255, 255, 255), font=_font(42))

    lines = [
        line.strip()
        for line in prompt[:180].split()
    ]
    wrapped = []
    current = ""
    for word in lines:
        if len(current) + len(word) + 1 <= 30:
            current = (current + " " + word).strip()
        else:
            wrapped.append(current)
            current = word
    if current:
        wrapped.append(current)

    text_y = 220
    for line in wrapped[:5]:
        draw.text((120, text_y), line, fill=(220, 230, 255), font=_font(26))
        text_y += 50

    image.save(path)
    return f"/static/panels/{filename}"
