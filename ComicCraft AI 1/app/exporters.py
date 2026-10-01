from datetime import datetime
from pathlib import Path

from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "static" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _get_unicode_font_name(pdf: FPDF) -> str:
    candidates = [
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\calibri.ttf"),
        Path(r"C:\Windows\Fonts\candara.ttf"),
    ]

    for font_path in candidates:
        if font_path.exists():
            try:
                pdf.add_font("ArialUnicode", "", str(font_path), uni=True)
                return "ArialUnicode"
            except Exception:
                continue

    return "Helvetica"


def save_pdf(layout):
    """Export a simple preview PDF into static/exports and return the download URL."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    output_path = EXPORT_DIR / filename

    pdf = FPDF()
    pdf.add_page()
    unicode_font = _get_unicode_font_name(pdf)
    pdf.set_font(unicode_font, "", 18)
    pdf.cell(0, 10, "ComicCraft Preview", new_x="LMARGIN", new_y="NEXT")

    for panel in layout:
        pdf.ln(6)
        pdf.set_font(unicode_font, "", 12)
        panel_name = panel.get("title", f"Panel {panel.get('panel_number', 1)}")
        pdf.cell(0, 8, f"Panel {panel.get('panel_number', 1)}: {panel_name}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(unicode_font, "", 10)
        pdf.multi_cell(0, 8, panel.get("scene_description", ""))

        image_url = panel.get("image_url", "")
        if image_url:
            image_name = image_url.rsplit("/", 1)[-1]
            image_path = BASE_DIR / "static" / "panels" / image_name
            if image_path.exists():
                pdf.image(str(image_path), x=10, y=pdf.get_y() + 4, w=180)
                pdf.ln(70)

    pdf.output(str(output_path))
    return f"/download/{filename}"
