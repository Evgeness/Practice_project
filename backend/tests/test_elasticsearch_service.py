from app.services.elasticsearch_service import ElasticsearchService


class FakeIndices:
    def __init__(self) -> None:
        self.created = None
        self.refreshed = None

    def exists(self, index: str) -> bool:
        return False

    def create(self, **kwargs) -> None:
        self.created = kwargs

    def refresh(self, index: str) -> None:
        self.refreshed = index


class FakeClient:
    def __init__(self) -> None:
        self.indices = FakeIndices()
        self.last_search = None

    def search(self, **kwargs):
        self.last_search = kwargs
        return {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_score": 2.5,
                        "_source": {
                            "chunk_id": "doc:1",
                            "document_id": "doc",
                            "file_name": "lecture.pdf",
                            "page_number": 2,
                            "text": "Полный текст фрагмента",
                        },
                        "highlight": {"text": ["[[HIGHLIGHT]]текст[[/HIGHLIGHT]]"]},
                    }
                ],
            }
        }

    def ping(self) -> bool:
        return True


def test_ensure_index_creates_russian_analyzer() -> None:
    service = ElasticsearchService("http://unused:9200", "documents")
    fake = FakeClient()
    service.client = fake
    service.ensure_index(max_attempts=1, delay_seconds=0)
    analyzer = fake.indices.created["settings"]["analysis"]["analyzer"]["analysis_ru"]
    assert "russian_stemmer" in analyzer["filter"]


def test_search_normalizes_elasticsearch_response() -> None:
    service = ElasticsearchService("http://unused:9200", "documents")
    fake = FakeClient()
    service.client = fake
    result = service.search("поиск", page=2, size=10)
    assert fake.last_search["from_"] == 10
    assert result["total"] == 1
    assert result["items"][0]["page"] == 2
    assert result["items"][0]["score"] == 2.5
    assert service.ping() is True