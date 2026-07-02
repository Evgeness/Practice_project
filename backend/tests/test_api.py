import asyncio
from io import BytesIO
from pathlib import Path

import pytest
from app.api.search import search_documents
from fastapi import HTTPException, UploadFile

from app.api.documents import upload_document
from app.core.config import Settings

FIXTURES = Path(__file__).parent / "fixtures"


class FakeDB:
    def __init__(self) -> None:
        self.objects = []
        self.commits = 0

    def add(self, value) -> None:
        self.objects.append(value)

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, value) -> None:
        return None


class FakeElasticsearch:
    def __init__(self) -> None:
        self.indexed = []
        self.search_calls = 0

    def index_chunks(self, chunks) -> None:
        self.indexed = chunks

    def search(self, query: str, page: int, size: int):
        self.search_calls += 1
        return {
            "total": 1,
            "items": [
                {
                    "chunk_id": "doc:1",
                    "document_id": "doc",
                    "file_name": "sample.docx",
                    "page": 1,
                    "text": "университетская база знаний",
                    "highlight": "[[HIGHLIGHT]]база[[/HIGHLIGHT]] знаний",
                    "score": 1.2,
                }
            ],
        }


class FakeCache:
    def __init__(self) -> None:
        self.values = {}

    def search_key(self, query: str, page: int, size: int) -> str:
        return f"{query}|{page}|{size}"

    def get_json(self, key: str):
        return self.values.get(key)

    def set_json(self, key: str, value) -> None:
        self.values[key] = value


def test_upload_endpoint_indexes_docx() -> None:
    db = FakeDB()
    elasticsearch = FakeElasticsearch()
    data = (FIXTURES / "sample.docx").read_bytes()
    upload = UploadFile(filename="sample.docx", file=BytesIO(data))
    settings = Settings(max_upload_mb=20, chunk_size=1000, chunk_overlap=100)

    result = asyncio.run(upload_document(upload, db, elasticsearch, settings))

    assert result.status == "ready"
    assert result.chunks_count >= 1
    assert elasticsearch.indexed[0]["file_name"] == "sample.docx"
    assert db.commits == 2


def test_upload_endpoint_rejects_txt() -> None:
    upload = UploadFile(filename="notes.txt", file=BytesIO(b"text"))
    with pytest.raises(HTTPException) as error:
        asyncio.run(upload_document(upload, FakeDB(), FakeElasticsearch(), Settings()))
    assert error.value.status_code == 400


def test_search_endpoint_uses_cache_after_first_request() -> None:
    db = FakeDB()
    elasticsearch = FakeElasticsearch()
    cache = FakeCache()

    first = search_documents("  база   знаний ", 1, 10, db, elasticsearch, cache)
    second = search_documents("база знаний", 1, 10, db, elasticsearch, cache)

    assert first.total == 1
    assert first.cached is False
    assert second.cached is True
    assert elasticsearch.search_calls == 1
    assert db.commits == 2
