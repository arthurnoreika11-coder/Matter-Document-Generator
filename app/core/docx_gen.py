from docx import Document

def create_lba(lba_name: str, recipient_name: str, legal_basis: str, demands: str) -> Document:
    doc = Document()

    doc.add_heading("Letter before Action", level=1)

    doc.add_paragraph(f"Dear {recipient_name},")
    doc.add_paragraph("Please accept this letter as a formal notice of my intention to take legal action.")
    doc.add_paragraph(f"Legal basis: {legal_basis}")
    doc.add_paragraph(f"Demands: {demands}")
    doc.add_paragraph("I request that you respond to this letter within 14 days of receipt. Failure to do so will result in further legal action.")

    doc.save(f'{lba_name}.docx')

    return doc


