def split_text(text, chunk_size=2500):
    """
    Split large document text into smaller chunks.

    Each chunk contains approximately chunk_size characters.
    The function tries to split at a sentence or word boundary.
    """

    if not text or not text.strip():
        return []

    text = text.strip()

    chunks = []

    while len(text) > chunk_size:

        split_at = text.rfind(".", 0, chunk_size)

        if split_at == -1:
            split_at = text.rfind(" ", 0, chunk_size)

        if split_at == -1:
            split_at = chunk_size

        chunk = text[:split_at + 1].strip()

        if chunk:
            chunks.append(chunk)

        text = text[split_at + 1:].strip()

    if text:
        chunks.append(text)

    return chunks