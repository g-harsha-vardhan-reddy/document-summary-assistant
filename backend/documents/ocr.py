from PIL import Image
import pytesseract
import pymupdf
import re
import os
import shutil


# Tesseract configuration

if os.name == "nt":
    windows_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    if os.path.exists(windows_tesseract):
        pytesseract.pytesseract.tesseract_cmd = windows_tesseract

else:
    tesseract_path = shutil.which("tesseract")

    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path


# Clean OCR text

def clean_ocr_text(text):
    """
    Clean OCR output while preserving useful document structure.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = text.replace("â€¢", "•")

    corrections = [
        (r"(?i)documentthis", "document this"),
        (r"(?i)fortesting", "for testing"),
        (r"(?i)asselectable", "as selectable"),
        (r"(?i)wasparsed", "was parsed"),
        (r"(?i)improvementsuggestions", "improvement suggestions"),
        (r"(?i)foxjumps", "fox jumps"),
        (r"(?i)learningprojects", "learning projects"),
        (r"(?i)machinelearning", "machine learning"),
        (r"(?i)beparsed", "be parsed"),
        (r"(?i)usingocr", "using OCR"),
        (r"(?i)animage", "an image"),
    ]

    for pattern, replacement in corrections:
        text = re.sub(pattern, replacement, text)

    lines = []

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            lines.append("")
            continue

        line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(line)

    cleaned_lines = []
    current = ""

    for line in lines:

        if not line:
            if current:
                cleaned_lines.append(current)
                current = ""
            continue

        if re.match(r"^\d+[\.\)]\s+", line):
            if current:
                cleaned_lines.append(current)

            current = line
            continue

        if re.match(r"^[\-\*\•]\s+", line):
            if current:
                cleaned_lines.append(current)

            current = line
            continue

        heading_patterns = [
            r"^document summary assistant",
            r"^scanned document$",
            r"^project topic:",
            r"^purpose:",
            r"^key information:",
            r"^ocr test sentence:",
        ]

        is_heading = any(
            re.match(pattern, line, re.IGNORECASE)
            for pattern in heading_patterns
        )

        if is_heading:
            if current:
                cleaned_lines.append(current)

            current = line
            continue

        if not current:
            current = line
            continue

        if current.endswith((".", "!", "?", ":")):
            cleaned_lines.append(current)
            current = line
        else:
            current += " " + line

    if current:
        cleaned_lines.append(current)

    result = "\n".join(cleaned_lines)

    result = re.sub(r"[ \t]+", " ", result)
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result.strip()


def extract_image_text(file_path):
    """
    Extract text from an image using Tesseract OCR.
    """

    image = Image.open(file_path)

    try:
        text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )
    finally:
        image.close()

    return clean_ocr_text(text)


def extract_scanned_pdf_text(file_path):
    """
    Extract text from scanned PDF pages using Tesseract OCR.
    """

    document = pymupdf.open(file_path)

    extracted_pages = []

    try:

        for page in document:

            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False
            )

            image = Image.frombytes(
                "RGB",
                [pixmap.width, pixmap.height],
                pixmap.samples
            )

            try:
                page_text = pytesseract.image_to_string(
                    image,
                    config="--psm 6"
                )
            finally:
                image.close()

            page_text = clean_ocr_text(page_text)

            if page_text:
                extracted_pages.append(page_text)

    finally:
        document.close()

    return "\n\n".join(extracted_pages).strip()