import tempfile
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from app.core.doc_gens.doc_setup import _safe_doc_filename

doc = SimpleDocTemplate(
    docTitle, 
    pagesize=letter,
    rightMargin=54, leftMargin=54, 
    topMargin=54, bottomMargin=54
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,        # Line spacing (must change if font size changes)
        spaceAfter=15,
        textColor='#1a365d' # Hex colors allowed
    )

body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=10
    )

def create_lba(lba_name: str,
    recipient_name: str,
    legal_basis: str,
    demands: str,
    output_dir: str | Path | None = None,
) -> Path:
    contents = []

    contents.append(Paragraph('Letter Before Action', title_style))
    contents.append(Spacer(1,10))
    contents.append(Paragraph(f"Dear {recipient_name},", body_style))
    contents.append(Paragraph("Please accept this letter as a formal notice of my intention to take legal action.", body_style))
    contents.append(Paragraph(f"Legal basis: {legal_basis}", body_style))
    contents.append(Paragraph(f"Demands: {demands}", body_style))
    contents.append(Paragraph("I request that you respond to this letter within 14 days of receipt. Failure to do so will result in further legal action.", body_style))

    target_dir = Path(output_dir) if output_dir is not None else Path(tempfile.mkdtemp(prefix="matter-pdf-"))
    target_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = target_dir / _safe_doc_filename(lba_name)

    doc.build(contents)

    return pdf_path