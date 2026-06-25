import re


def normalize_text(text: str) -> str:
    """Collapse whitespace while preserving readable paragraph breaks."""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks without cutting words when possible.

    Args:
        text: Source text.
        chunk_size: Maximum target chunk size in characters.
        overlap: Number of characters repeated between neighboring chunks.

    Returns:
        A list of non-empty text chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    normalized = normalize_text(text)
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    length = len(normalized)

    while start < length:
        target_end = min(start + chunk_size, length)
        end = target_end

        if target_end < length:
            word_break = normalized.rfind(" ", start + int(chunk_size * 0.7), target_end)
            if word_break > start:
                end = word_break

        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= length:
            break

        next_start = max(0, end - overlap)
        if next_start <= start:
            next_start = end
        start = next_start

    return chunks
