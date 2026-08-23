import re


def generate_suggestions(text):
    """
    Generate improvement suggestions based on document content.
    """

    if not text or not text.strip():
        return []

    text = text.strip()

    suggestions = []

    lower_text = text.lower()

    # 1. DOCUMENT LENGTH

    word_count = len(text.split())

    if word_count < 100:
        suggestions.append(
            "The document is quite short. Consider adding more relevant "
            "details or supporting information."
        )

    # 2. STRUCTURE

    if not any(
        keyword in lower_text
        for keyword in [
            "introduction",
            "overview",
            "summary",
            "conclusion",
            "objective",
            "purpose",
        ]
    ):
        suggestions.append(
            "Consider adding clear sections such as an introduction, "
            "main content, and conclusion to improve document structure."
        )

    # 3. NUMBERED / BULLET INFORMATION

    has_bullets = bool(
        re.search(
            r"(^|\n)\s*[-•*]\s+",
            text
        )
    )

    has_numbered_items = bool(
        re.search(
            r"(^|\n)\s*\d+[\.\)]\s+",
            text
        )
    )

    if not has_bullets and not has_numbered_items:
        suggestions.append(
            "Consider using bullet points or numbered lists for "
            "important information to improve readability."
        )

    # 4. VERY LONG SENTENCES
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    long_sentences = 0

    for sentence in sentences:

        if len(sentence.split()) > 35:
            long_sentences += 1

    if long_sentences > 0:
        suggestions.append(
            "Some sentences are quite long. Consider breaking them "
            "into shorter sentences for better readability."
        )
    # 5. REPEATED WORDS

    words = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        lower_text
    )

    word_frequency = {}

    for word in words:

        word_frequency[word] = (
            word_frequency.get(word, 0) + 1
        )

    repeated_words = [
        word
        for word, frequency in word_frequency.items()
        if frequency > 10
    ]

    if repeated_words:

        suggestions.append(
            "Some words are repeated frequently. Consider varying "
            "the wording where appropriate."
        )

    # 6. OCR QUALITY

    ocr_patterns = [
        "documentcreated",
        "andlong",
        "thefinal",
        "thesummary",
        "theproject",
    ]

    ocr_errors = 0

    for pattern in ocr_patterns:

        if pattern in lower_text:
            ocr_errors += 1

    if ocr_errors > 0:

        suggestions.append(
            "The extracted text contains possible OCR formatting "
            "issues. Consider reviewing the original document for accuracy."
        )

    # 7. GENERAL CLARITY

    if word_count >= 100:

        suggestions.append(
            "Consider highlighting the most important information "
            "using headings, bullet points, or concise summaries."
        )

    # 8. FINAL FALLBACK

    if not suggestions:

        suggestions.append(
            "The document is reasonably structured. Consider reviewing "
            "clarity, consistency, formatting, and grammar before final use."
        )

    # Return maximum 5 suggestions
    return suggestions[:5]