from pathlib import Path

import pytest

from app.services.document_parser import (
    DocumentValidationError,
    parse_document,
    validate_upload,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_validate_upload_accepts_pdf_and_sanitizes_name() -> None:
    name, file_type = validate_upload("../lecture.PDF", b"123")
    assert name == "lecture.PDF"
    assert file_type == "pdf"


@pytest.mark.parametrize("file_name", ["notes.txt", "archive.zip", "image.png"])
def test_validate_upload_rejects_extension(file_name: str) -> None:
    with pytest.raises(DocumentValidationError, match="PDF и DOCX"):
        validate_upload(file_name, b"content")


def test_validate_upload_rejects_empty_file() -> None:
    with pytest.raises(DocumentValidationError, match="пуст"):
        validate_upload("empty.pdf", b"")


def test_validate_upload_rejects_oversized_file() -> None:
    with pytest.raises(DocumentValidationError, match="превышает"):
        validate_upload("large.pdf", b"x" * 1025, max_upload_mb=0)


def test_parse_docx_extracts_text() -> None:
    data = (FIXTURES / "sample.docx").read_bytes()
    pages = parse_document("sample.docx", data)
    assert pages[0][0] == 1
    assert "университетская база знаний" in pages[0][1].lower()


def test_parse_pdf_extracts_text() -> None:
    data = (FIXTURES / "sample.pdf").read_bytes()
    pages = parse_document("sample.pdf", data)
    assert pages[0][0] == 1
    assert "knowledge search" in pages[0][1].lower()


def test_parse_broken_document_returns_validation_error() -> None:
    with pytest.raises(DocumentValidationError, match="Не удалось прочитать"):
        parse_document("broken.pdf", (FIXTURES / "broken.pdf").read_bytes())
