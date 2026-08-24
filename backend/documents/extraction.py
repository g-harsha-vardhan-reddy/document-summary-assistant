import pymupdf


def extract_pdf_text(file_path):
    """
    Extract selectable text from a PDF.
    """

    document = pymupdf.open(file_path)

    text = ""

    try:
        for page in document:
            text += page.get_text()
            text += "\n"
    finally:
        document.close()

    return text.strip()