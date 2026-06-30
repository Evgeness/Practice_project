import pytest

from app.services.chunking import chunk_text, normalize_text


def test_normalize_text_removes_repeated_whitespace() -> None:
    assert normalize_text("  one   two\n\n\nthree  ") == "one two\n\nthree"


def test_short_text_is_one_chunk() -> None:
    assert chunk_text("короткий текст", chunk_size=100, overlap=10) == ["короткий текст"]


def test_chunks_have_overlap_and_cover_tail() -> None:
    text = " ".join(f"слово{i}" for i in range(150))
    chunks = chunk_text(text, chunk_size=120, overlap=20)
    assert len(chunks) > 5
    assert chunks[-1].endswith("слово149")
    assert all(len(chunk) <= 120 for chunk in chunks)
    assert any(chunks[index][-10:] in chunks[index + 1] for index in range(len(chunks) - 1))


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [(0, 0), (100, -1), (100, 100), (100, 101)],
)
def test_invalid_chunk_arguments(chunk_size: int, overlap: int) -> None:
    with pytest.raises(ValueError):
        chunk_text("text", chunk_size=chunk_size, overlap=overlap)
