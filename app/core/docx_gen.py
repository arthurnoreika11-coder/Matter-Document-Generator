from docx import Document

def create_doc(doc_name):
    doc = Document()

    doc.add_heading(doc_name, 0)

    doc.save(f'{doc_name}.docx')


