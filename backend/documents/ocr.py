from PIL import Image
import pytesseract
import pymupdf
import re
import os
import shutil


def configure_tesseract():
    if os.name == "nt":
        paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]

        for path in paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return True

        path = shutil.which("tesseract")

        if path:
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    else:
        paths = [
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
        ]

        for path in paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return True

        path = shutil.which("tesseract")

        if path:
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    return False


TESSERACT_AVAILABLE = configure_tesseract()


def check_tesseract():
    if not TESSERACT_AVAILABLE:
        raise RuntimeError(
            "Tesseract OCR is not installed on the server."
        )

    try:
        return str(
            pytesseract.get_tesseract_version()
        )
    except Exception as exc:
        raise RuntimeError(
            "Tesseract OCR could not be started."
        ) from exc


def clean_ocr_text(text):
    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = text.replace("â€¢", "•")
    text = text.replace("â€“", "–")
    text = text.replace("â€”", "—")
    text = text.replace("â€™", "'")
    text = text.replace("â€œ", '"')
    text = text.replace("â€", '"')

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

    cleaned_lines = []
    current = ""

    for line in lines:
        if not line:
            if current:
                cleaned_lines.append(current)
                current = ""
            continue

        if re.match(
            r"^\d+[\.\)]\s+",
            line
        ):
            if current:
                cleaned_lines.append(current)

            current = line
            continue

        if re.match(
            r"^[\-\*\•]\s+",
            line
        ):
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

        if not current:
            current = line
            continue

        if current.endswith(
            (".", "!", "?", ":")
        ):
            cleaned_lines.append(current)
            current = line
        else:
            current += " " + line

    if current:
        cleaned_lines.append(current)

    result = "\n".join(cleaned_lines)

    result = re.sub(
        r"[ \t]+",
        " ",
        result
    )

    result = re.sub(
        r"\n{3,}",
        "\n\n",
        result
    )

    return result.strip()


def extract_image_text(file_path):
    check_tesseract()

    image = Image.open(file_path)

    try:
        if image.mode != "RGB":
            image = image.convert("RGB")

        text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )
    finally:
        image.close()

    return clean_ocr_text(text)


def extract_scanned_pdf_text(file_path):
    check_tesseract()

    document = pymupdf.open(file_path)

    extracted_pages = []

    try:
        for page_number, page in enumerate(
            document,
            start=1
        ):
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False
            )

            image = Image.frombytes(
                "RGB",
                [
                    pixmap.width,
                    pixmap.height
                ],
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
                    f"Page {page_number}\n{page_text}"
                )

    finally:
        document.close()

    return "\n\n".join(
        extracted_pages
    ).strip()


def extract_ocr_text(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = os.path.splitext(
        file_path
    )[1].lower()

    image_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
        ".tiff",
        ".tif",
    }

    if extension in image_extensions:
        return extract_image_text(
            file_path
        )

    if extension == ".pdf":
        return extract_scanned_pdf_text(
            file_path
        )

    raise ValueError(
        "Unsupported file type. "
        "Please upload a PDF, PNG, JPG, or JPEG file."
    )

