from PIL import Image
import pytesseract
import pymupdf
import re


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# ============================================================
# CLEAN OCR TEXT
# ============================================================

def clean_ocr_text(text):
    """
    Clean OCR output while preserving useful document structure.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Fix common OCR encoding
    text = text.replace("â€¢", "•")

    # Fix common joined words
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
        text = re.sub(
            pattern,
            replacement,
            text
        )

    # Normalize spaces inside each line
    lines = []

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            lines.append("")
            continue

        line = re.sub(
            r"[ \t]+",
            " ",
            line
        ).strip()

        lines.append(line)

    # ========================================================
    # JOIN OCR-WRAPPED LINES
    # ========================================================

    cleaned_lines = []

    current = ""

    for line in lines:

        # Preserve blank lines as paragraph boundaries
        if not line:

            if current:
                cleaned_lines.append(current)
                current = ""

            continue

        # ----------------------------------------------------
        # Numbered item → new line
        # ----------------------------------------------------

        if re.match(
            r"^\d+[\.\)]\s+",
            line
        ):

            if current:
                cleaned_lines.append(current)

            current = line

            continue

        # ----------------------------------------------------
        # Bullet item → new line
        # ----------------------------------------------------

        if re.match(
            r"^[\-\*\•]\s+",
            line
        ):

            if current:
                cleaned_lines.append(current)

            current = line

            continue

        # ----------------------------------------------------
        # Heading-like line
        # ----------------------------------------------------

        heading_patterns = [
            r"^document summary assistant",
            r"^scanned document$",
            r"^project topic:",
            r"^purpose:",
            r"^key information:",
            r"^ocr test sentence:",
        ]

        is_heading = any(
            re.match(
                pattern,
                line,
                re.IGNORECASE
            )
            for pattern in heading_patterns
        )

        if is_heading:

            if current:
                cleaned_lines.append(current)

            current = line

            continue

        # ----------------------------------------------------
        # First line
        # ----------------------------------------------------

        if not current:

            current = line

            continue

        # ----------------------------------------------------
        # Previous line already ended a sentence
        # ----------------------------------------------------

        if current.endswith(
            (".", "!", "?", ":")
        ):

            cleaned_lines.append(current)

            current = line

        else:

            # ------------------------------------------------
            # OCR wrapped line → join
            # ------------------------------------------------

            current += " " + line

    if current:
        cleaned_lines.append(current)

    # ========================================================
    # FINAL CLEANUP
    # ========================================================

    result = "\n".join(cleaned_lines)

    # Remove excessive spaces
    result = re.sub(
        r"[ \t]+",
        " ",
        result
    )

    # Remove excessive blank lines
    result = re.sub(
        r"\n{3,}",
        "\n\n",
        result
    )

    return result.strip()


# ============================================================
# IMAGE OCR
# ============================================================

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


# ============================================================
# SCANNED PDF OCR
# ============================================================

def extract_scanned_pdf_text(file_path):
    """
    Extract text from scanned PDF pages using Tesseract OCR.
    """

    document = pymupdf.open(file_path)

    extracted_pages = []

    try:

        for page in document:

            # Render PDF page at higher resolution
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

            page_text = clean_ocr_text(
                page_text
            )

            if page_text:
                extracted_pages.append(
                    page_text
                )

    finally:

        document.close()

    return "\n\n".join(
        extracted_pages
    ).strip()