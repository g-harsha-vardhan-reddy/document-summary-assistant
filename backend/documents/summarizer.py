from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re

from .chunker import split_text


# MODEL

MODEL_NAME = "facebook/bart-large-cnn"

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME
)


# SUMMARY SETTINGS

SUMMARY_SENTENCE_LIMITS = {
    "short": 2,
    "medium": 4,
    "long": 6,
}

# CLEAN DOCUMENT

def clean_document_text(text):
    """
    Remove headings and obvious OCR test content while
    preserving the actual document information.
    """

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        # Remove standalone headings
        if lower in {
            "scanned document",
            "key information",
            "document summary assistant",
        }:
            continue

        # Remove OCR test sentence
        if lower.startswith(
            "ocr test sentence:"
        ):
            continue

        # Remove project heading
        if lower.startswith(
            "project topic:"
        ):
            continue

        # Convert purpose heading into content
        if lower.startswith("purpose:"):

            parts = line.split(
                ":",
                1
            )

            if len(parts) == 2:

                content = parts[1].strip()

                if content:
                    lines.append(content)

            continue

        lines.append(line)

    cleaned = " ".join(lines)

    # Normalize spaces
    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    ).strip()

    return cleaned

# EXTRACT SENTENCES

def extract_sentences(text):
    """
    Extract complete sentences from document text.
    """

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    result = []

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        if len(sentence.split()) < 6:
            continue

        result.append(sentence)

    return result

# SCORE IMPORTANT SENTENCES

def score_sentences(sentences):
    """
    Rank sentences by relevance to document summarization.
    """

    keywords = [
        "document",
        "pdf",
        "image",
        "ocr",
        "extract",
        "text",
        "summary",
        "summaries",
        "application",
        "project",
        "process",
        "processed",
        "parse",
        "parsed",
        "support",
        "generate",
        "generated",
        "key points",
        "suggestions",
        "improvement",
    ]

    action_words = [
        "extract",
        "extracted",
        "process",
        "processed",
        "parse",
        "parsed",
        "generate",
        "generated",
        "support",
        "include",
        "create",
        "created",
    ]

    scored = []

    for index, sentence in enumerate(sentences):

        lower = sentence.lower()

        score = 0

        # Keyword relevance
        for keyword in keywords:

            if keyword in lower:
                score += 2

        # Action / functionality
        for word in action_words:

            if word in lower:
                score += 2
                break

        # Prefer useful sentence length
        word_count = len(
            sentence.split()
        )

        if 8 <= word_count <= 30:
            score += 2

        # Prefer complete sentences
        if sentence.endswith(
            (".", "!", "?")
        ):
            score += 1

        scored.append(
            (
                score,
                index,
                sentence
            )
        )

    scored.sort(
        key=lambda item: (
            -item[0],
            item[1]
        )
    )

    return scored

# SMALL DOCUMENT SUMMARY

def summarize_small_document(
    text,
    length
):
    """
    Generate clearly different summaries for small documents.
    """

    sentences = extract_sentences(
        text
    )

    if not sentences:
        return ""

    scored = score_sentences(
        sentences
    )

    sentence_limit = SUMMARY_SENTENCE_LIMITS.get(
        length,
        SUMMARY_SENTENCE_LIMITS["medium"]
    )

    # Take the most important sentences
    selected = scored[:sentence_limit]

    # Restore original document order
    selected.sort(
        key=lambda item: item[1]
    )

    summary_sentences = [
        item[2]
        for item in selected
    ]

    return " ".join(
        summary_sentences
    )


# BART SUMMARY FOR LARGE DOCUMENTS


def summarize_chunk(
    text,
    length="medium"
):
    """
    Summarize a large document chunk using BART.
    """

    if not text or not text.strip():
        return ""

    text = text.strip()

    if length == "short":

        max_length = 80
        min_length = 20

    elif length == "long":

        max_length = 180
        min_length = 50

    else:

        max_length = 120
        min_length = 30

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    )

    input_tokens = inputs[
        "input_ids"
    ].shape[1]

    # Prevent invalid generation limits
    max_length = min(
        max_length,
        max(20, int(input_tokens * 0.75))
    )

    min_length = min(
        min_length,
        max(10, int(input_tokens * 0.25))
    )

    if min_length >= max_length:
        min_length = max(
            5,
            max_length // 2
        )

    outputs = model.generate(
        **inputs,

        max_length=max_length,
        min_length=min_length,

        num_beams=4,

        do_sample=False,

        no_repeat_ngram_size=3,

        repetition_penalty=1.1,

        length_penalty=1.0,

        early_stopping=True
    )

    return tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    ).strip()

# COMPLETE SUMMARY


def generate_summary(
    text,
    length="medium"
):
    """
    Generate short, medium, or long summaries.

    Small documents:
        Sentence-selection based summary.

    Large documents:
        Chunking + BART summarization.
    """

    if not text or not text.strip():
        return ""

    if length not in {
        "short",
        "medium",
        "long"
    }:
        length = "medium"

    # CLEAN DOCUMENT


    cleaned_text = clean_document_text(
        text
    )

    if not cleaned_text:
        return ""

    # SPLIT DOCUMENT


    chunks = split_text(
        cleaned_text,
        chunk_size=2500
    )

    if not chunks:
        return ""

    # SMALL DOCUMENT
 
    if len(chunks) == 1:

        return summarize_small_document(
            cleaned_text,
            length
        )

    # LARGE DOCUMENT

    chunk_summaries = []

    for chunk in chunks:

        summary = summarize_chunk(
            chunk,
            length
        )

        if summary:
            chunk_summaries.append(
                summary
            )

    if not chunk_summaries:
        return ""

    combined_text = " ".join(
        chunk_summaries
    )


    # FINAL LARGE-DOCUMENT SUMMARY

    final_summary = summarize_chunk(
        combined_text,
        length
    )

    return final_summary