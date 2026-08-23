import re


# TEXT CLEANING

def clean_text(text):
    """
    Clean common OCR formatting problems.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Fix common OCR encoding
    text = text.replace("â€¢", "•")

    # Common joined OCR words
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
        (r"(?i)imageconversion", "image conversion"),
        (r"(?i)imagetype", "image type"),
        (r"(?i)imageprocessing", "image processing"),
        (r"(?i)imageshould", "image should"),
    ]

    for pattern, replacement in corrections:
        text = re.sub(
            pattern,
            replacement,
            text
        )

    # Add missing space after punctuation
    text = re.sub(
        r"([.!?])([A-Za-z])",
        r"\1 \2",
        text
    )

    # Normalize spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Normalize excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# HEADING / METADATA DETECTION

def is_heading_or_metadata(text):
    """
    Detect headings, metadata, formatting lines, and other
    non-content lines that should not become key points.
    """

    if not text:
        return True

    value = text.strip()
    lower = value.lower()

    # Common headings
    heading_patterns = [
        r"^key information:?$",
        r"^scanned document$",
        r"^project topic:?$",
        r"^purpose:?$",
        r"^document summary assistant$",
        r"^document summary assistant\s*-\s*.*$",
        r"^ocr test sentence:?$",
        r"^methodology\s*/?\s*theory:?$",
        r"^methodology:?$",
        r"^theory:?$",
        r"^aim:?$",
        r"^software required:?$",
        r"^function used:?$",
    ]

    for pattern in heading_patterns:
        if re.match(
            pattern,
            value,
            re.IGNORECASE
        ):
            return True

    # Document metadata
    metadata_patterns = [
        r"^name\s*[:\-]",
        r"^date\s*[:\-]",
        r"^reg\s*\.?\s*no\s*[:\-]",
        r"^registration\s*no\s*[:\-]",
        r"^lab\s*[:\-]",
        r"^section\s*[:\-]",
        r"^roll\s*no\s*[:\-]",
        r"^student\s*name\s*[:\-]",
        r"^course\s*[:\-]",
        r"^subject\s*[:\-]",
    ]

    for pattern in metadata_patterns:
        if re.search(
            pattern,
            value,
            re.IGNORECASE
        ):
            return True

    # Decorative-only lines
    if not re.search(
        r"[A-Za-z]{2,}",
        value
    ):
        return True

    cleaned_symbols = re.sub(
        r"[\s=\-_.:<>/\\|]+",
        "",
        value
    )

    if len(cleaned_symbols) < 5:
        return True

    return False

# SOFTWARE / TOOL LIST DETECTION

def is_software_only(text):
    """
    Detect lines that contain only software/tool names,
    labels, bullets, or decorative OCR characters.
    """

    if not text:
        return True

    value = text.strip()

    # Remove common decorative OCR characters
    cleaned = re.sub(
        r"[-\\•*|=<>:]+",
        " ",
        value
    )

    # Normalize spaces
    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    ).strip()

    # Remove the Software Required label
    cleaned = re.sub(
        r"(?i)^software\s+required\s*",
        "",
        cleaned
    ).strip()

    # Remove common tool names
    remaining = cleaned

    remaining = re.sub(
        r"(?i)\bmatlab\b",
        "",
        remaining
    )

    remaining = re.sub(
        r"(?i)\bimage\s+processing\s+toolbox\b",
        "",
        remaining
    )

    remaining = re.sub(
        r"\s+",
        " ",
        remaining
    ).strip()

    # If nothing meaningful remains, it's a software-only line
    if not remaining:
        return True

    return False


# ============================================================
# BUILD OCR BLOCKS
# ============================================================

def build_blocks(text):
    """
    Join OCR-wrapped lines into meaningful blocks.
    """

    if not text:
        return []

    lines = []

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"\s+",
            " ",
            line
        ).strip()

        if not line:
            continue

        lines.append(line)

    blocks = []

    current = ""

    for line in lines:

        # ----------------------------------------------------
        # Numbered item
        # ----------------------------------------------------

        if re.match(
            r"^\d+[\.\)]\s+",
            line
        ):

            if current:
                blocks.append(current)

            current = line

            continue

        # ----------------------------------------------------
        # Bullet item
        # ----------------------------------------------------

        if re.match(
            r"^[\-\*\•]\s+",
            line
        ):

            if current:
                blocks.append(current)

            current = line

            continue

        # ----------------------------------------------------
        # Heading / metadata
        # ----------------------------------------------------

        if is_heading_or_metadata(line):

            # Preserve actual content after Purpose:
            if line.lower().startswith(
                "purpose:"
            ):

                parts = line.split(
                    ":",
                    1
                )

                if len(parts) == 2:

                    content = parts[1].strip()

                    if content:

                        if current:
                            current += " " + content

                        else:
                            current = content

            continue

        # ----------------------------------------------------
        # First useful line
        # ----------------------------------------------------

        if not current:

            current = line

            continue

        # ----------------------------------------------------
        # Previous sentence finished
        # ----------------------------------------------------

        if current.endswith(
            (".", "!", "?", ":")
        ):

            blocks.append(current)

            current = line

        else:

            # OCR wrapped line
            current += " " + line

    if current:
        blocks.append(current)

    return blocks


# ============================================================
# GET CANDIDATES
# ============================================================

def get_candidates(text):
    """
    Extract complete and meaningful sentences/points.
    """

    if not text:
        return []

    text = clean_text(text)

    blocks = build_blocks(text)

    candidates = []

    for block in blocks:

        # ----------------------------------------------------
        # Normalize block
        # ----------------------------------------------------

        block = re.sub(
            r"\s+",
            " ",
            block
        ).strip()

        # Remove bullets
        block = re.sub(
            r"^[\-\*\•\|]+\s*",
            "",
            block
        ).strip()

        # Remove numbered prefixes
        block = re.sub(
            r"^\d+[\.\)]\s*",
            "",
            block
        ).strip()

        # ----------------------------------------------------
        # Remove joined section headings
        # ----------------------------------------------------

        block = re.sub(
            r"(?i)software\s+required\s*:\s*",
            "",
            block
        )

        block = re.sub(
            r"(?i)methodology\s*/?\s*theory\s*:\s*",
            "",
            block
        )

        block = block.strip()

        # ----------------------------------------------------
        # Skip software-only block
        # ----------------------------------------------------

        if is_software_only(block):
            continue

        # ----------------------------------------------------
        # Split into complete sentences
        # ----------------------------------------------------

        sentences = re.split(
            r"(?<=[.!?])\s+",
            block
        )

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            sentence = re.sub(
                r"\s+",
                " ",
                sentence
            ).strip()

            # Skip headings
            if is_heading_or_metadata(
                sentence
            ):
                continue

            # Skip software/tool lists
            if is_software_only(sentence):
                continue

            words = sentence.split()

            # Ignore tiny fragments
            if len(words) < 7:
                continue

            # Ignore very large blocks
            if len(words) > 40:
                continue

            candidates.append(sentence)

    return candidates


# ============================================================
# GENERATE KEY POINTS
# ============================================================

def generate_key_points(text, count=5):
    """
    Extract up to `count` important key points.
    """

    if not text or not text.strip():
        return []

    cleaned = clean_text(text)

    candidates = get_candidates(
        cleaned
    )

    if not candidates:
        return []

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    unique = []
    seen = set()

    for candidate in candidates:

        normalized = re.sub(
            r"\s+",
            " ",
            candidate.lower()
        ).strip()

        if normalized in seen:
            continue

        seen.add(normalized)

        unique.append(candidate)

    # --------------------------------------------------------
    # IMPORTANT CONTENT KEYWORDS
    # --------------------------------------------------------

    keywords = [
        "aim",
        "purpose",
        "objective",
        "project",
        "experiment",
        "methodology",
        "process",
        "processed",
        "perform",
        "performed",
        "generate",
        "generated",
        "extract",
        "extracted",
        "convert",
        "conversion",
        "converted",
        "transform",
        "transformation",
        "image",
        "pdf",
        "ocr",
        "summary",
        "key points",
        "suggestions",
        "matlab",
        "python",
        "java",
        "django",
        "flask",
        "api",
        "machine learning",
        "data",
    ]

    # --------------------------------------------------------
    # ACTION WORDS
    # --------------------------------------------------------

    action_words = [
        "perform",
        "performed",
        "develop",
        "developed",
        "build",
        "built",
        "create",
        "created",
        "implement",
        "implemented",
        "process",
        "processed",
        "extract",
        "extracted",
        "convert",
        "converted",
        "generate",
        "generated",
        "display",
        "displayed",
        "load",
        "loaded",
    ]

    scored = []

    # --------------------------------------------------------
    # SCORE CANDIDATES
    # --------------------------------------------------------

    for index, candidate in enumerate(
        unique
    ):

        lower = candidate.lower()

        score = 0

        # Keyword relevance
        for keyword in keywords:

            if keyword in lower:
                score += 2

        # Action words
        for action in action_words:

            if action in lower:

                score += 2

                break

        # Useful sentence length
        word_count = len(
            candidate.split()
        )

        if 8 <= word_count <= 30:

            score += 3

        elif 31 <= word_count <= 40:

            score += 1

        # Prefer complete sentences
        if candidate.endswith(
            (".", "!", "?")
        ):

            score += 1

        scored.append(
            (
                score,
                index,
                candidate
            )
        )

    # --------------------------------------------------------
    # SORT BY IMPORTANCE
    # --------------------------------------------------------

    scored.sort(
        key=lambda item: (
            -item[0],
            item[1]
        )
    )

    # --------------------------------------------------------
    # SELECT TOP POINTS
    # --------------------------------------------------------

    selected = []

    for score, index, candidate in scored:

        selected.append(candidate)

        if len(selected) >= count:
            break

    # --------------------------------------------------------
    # RESTORE DOCUMENT ORDER
    # --------------------------------------------------------

    selected.sort(
        key=lambda candidate:
        unique.index(candidate)
    )

    return selected