from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re

from .chunker import split_text


# Model

MODEL_NAME = "sshleifer/distilbart-cnn-6-6"

tokenizer = None
model = None


# Summary settings

SUMMARY_SETTINGS = {
    "short": {
        "sentences": 3,
        "max_length": 80,
        "min_length": 25,
    },
    "medium": {
        "sentences": 7,
        "max_length": 140,
        "min_length": 45,
    },
    "long": {
        "sentences": 10,
        "max_length": 200,
        "min_length": 65,
    },
}


# Load model only when required

def load_model():

    global tokenizer
    global model

    if tokenizer is None or model is None:

        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )

        model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_NAME
        )

        model.eval()


# Clean document

def clean_document_text(text):

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if lower in {
            "scanned document",
            "key information",
            "document summary assistant",
        }:
            continue

        if lower.startswith(
            "ocr test sentence:"
        ):
            continue

        if lower.startswith(
            "project topic:"
        ):
            continue

        if lower.startswith(
            "purpose:"
        ):

            parts = line.split(
                ":",
                1
            )

            if len(parts) == 2:

                content = parts[1].strip()

                if content:
                    lines.append(
                        content
                    )

            continue

        lines.append(line)

    cleaned = " ".join(lines)

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    ).strip()

    return cleaned


# Extract sentences

def extract_sentences(text):

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

        if len(sentence.split()) < 5:
            continue

        result.append(sentence)

    return result


# Score important sentences

def score_sentences(sentences):

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

    for index, sentence in enumerate(
        sentences
    ):

        lower = sentence.lower()

        score = 0

        for keyword in keywords:

            if keyword in lower:
                score += 2

        for word in action_words:

            if word in lower:
                score += 2
                break

        word_count = len(
            sentence.split()
        )

        if 8 <= word_count <= 30:
            score += 2

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


# Small document summary

def summarize_small_document(
    text,
    length
):

    sentences = extract_sentences(
        text
    )

    if not sentences:
        return ""

    required_sentences = SUMMARY_SETTINGS[
        length
    ]["sentences"]

    required_sentences = min(
        required_sentences,
        len(sentences)
    )

    scored = score_sentences(
        sentences
    )

    selected = scored[
        :required_sentences
    ]

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


# BART summary

def summarize_chunk(
    text,
    length="medium"
):

    if not text or not text.strip():
        return ""

    load_model()

    text = text.strip()

    settings = SUMMARY_SETTINGS[
        length
    ]

    max_length = settings[
        "max_length"
    ]

    min_length = settings[
        "min_length"
    ]

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=768
    )

    input_tokens = inputs[
        "input_ids"
    ].shape[1]

    max_length = min(
        max_length,
        max(
            30,
            int(input_tokens * 0.70)
        )
    )

    min_length = min(
        min_length,
        max(
            15,
            int(input_tokens * 0.20)
        )
    )

    if min_length >= max_length:

        min_length = max(
            10,
            max_length // 2
        )

    outputs = model.generate(
        **inputs,
        max_length=max_length,
        min_length=min_length,
        num_beams=2,
        do_sample=False,
        no_repeat_ngram_size=3,
        repetition_penalty=1.1,
        length_penalty=1.0,
        early_stopping=True
    )

    summary = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    ).strip()

    return summary


# Control summary length

def control_summary_length(
    summary,
    length
):

    if not summary:
        return ""

    sentences = extract_sentences(
        summary
    )

    if not sentences:
        return summary

    sentence_limit = SUMMARY_SETTINGS[
        length
    ]["sentences"]

    return " ".join(
        sentences[:sentence_limit]
    )


# Generate summary

def generate_summary(
    text,
    length="medium"
):

    if not text or not text.strip():
        return ""

    if length not in {
        "short",
        "medium",
        "long"
    }:
        length = "medium"

    cleaned_text = clean_document_text(
        text
    )

    if not cleaned_text:
        return ""

    chunks = split_text(
        cleaned_text,
        chunk_size=2000
    )

    if not chunks:
        return ""

    # Small document

    if len(chunks) == 1:

        return summarize_small_document(
            cleaned_text,
            length
        )

    # Large document

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

    final_summary = summarize_chunk(
        combined_text,
        length
    )

    final_summary = control_summary_length(
        final_summary,
        length
    )

    return final_summary