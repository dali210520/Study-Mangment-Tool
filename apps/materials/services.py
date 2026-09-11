"""
PDF utility functions for study materials.
"""
from pypdf import PdfReader


def extract_pdf_text(file_obj):
    """
    Extract text and page count from a PDF file object.

    Returns:
        tuple[str, int]: Extracted text and number of pages.
    """
    file_obj.seek(0)
    reader = PdfReader(file_obj)
    page_texts = []

    for page in reader.pages:
        page_text = page.extract_text() or ''
        page_texts.append(page_text.strip())

    file_obj.seek(0)
    return '\n\n'.join(text for text in page_texts if text), len(reader.pages)
