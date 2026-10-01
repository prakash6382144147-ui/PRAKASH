import unicodedata
from pathlib import Path
from uuid import uuid4

from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "static" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _safe_pdf_text(value):
    text = str(value or "")
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("latin-1", "replace").decode("latin-1")
    return text


def save_pdf(layout):
    """Save a simple PDF from the generated comic layout."""
    filename = f"{uuid4().hex}.pdf"
    file_path = EXPORT_DIR / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    content_width = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(content_width, 12, _safe_pdf_text("ComicCraft Story"), ln=True)

    for panel in layout:
        title = _safe_pdf_text(panel.get("title", "Untitled Panel"))
        scene = _safe_pdf_text(panel.get("scene_description", ""))
        number = panel.get("panel_number", "")

        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(content_width, 8, f"Panel {number}: {title}")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(content_width, 8, scene)

    pdf.output(str(file_path))
    return f"/download/{filename}"
