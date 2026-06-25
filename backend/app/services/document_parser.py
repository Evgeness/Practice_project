from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pdfplumber
from docx import Document as DocxDocument


class DocumentValidationError(ValueError):
    """Raised when an uploaded document is invalid or unreadable."""


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def validate_upload(file_name: str | None, data: bytes, max_upload_mb: int = 20) -> tuple[str, str]:
    """Validate filename, extension, size and emptiness.

    Returns:
        A safe basename and a lowercase extension without the leading dot.
    """
    if not file_name:
        raise DocumentValidationError("Имя файла отсутствует")

    safe_name = Path(file_name).name
    extension = Path(safe_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise DocumentValidationError("Разрешены только файлы PDF и DOCX")

    if not data:
        raise DocumentValidationError("Файл пуст")

    max_size = max_upload_mb * 1024 * 1024
    if len(data) > max_size:
        raise DocumentValidationError(f"Размер файла превышает {max_upload_mb} МБ")

    return safe_name, extension.lstrip(".")


def parse_document(file_name: str, data: bytes) -> list[tuple[int, str]]:
    """Extract page-aware text from PDF or paragraph text from DOCX."""
    extension = Path(file_name).suffix.lower()
    try:
        if extension == ".pdf":
            pages = _parse_pdf(data)
        elif extension == ".docx":
            pages = _parse_docx(data)
        else:
            raise DocumentValidationError("Неподдерживаемый формат файла")
    except DocumentValidationError:
        raise
    except Exception as exc:
        raise DocumentValidationError(f"Не удалось прочитать документ: {exc}") from exc

    if not any(text.strip() for _, text in pages):
        raise DocumentValidationError("В документе не найден текст")
    return pages


def _parse_pdf(data: bytes) -> list[tuple[int, str]]:
    pages: list[tuple[int, str]] = []
    with pdfplumber.open(BytesIO(data)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            pages.append((page_number, page.extract_text() or ""))
    return pages


def _parse_docx(data: bytes) -> list[tuple[int, str]]:
    document = DocxDocument(BytesIO(data))
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    # DOCX does not expose reliable rendered page numbers without a layout engine.
    return [(1, "\n".join(paragraphs))]
