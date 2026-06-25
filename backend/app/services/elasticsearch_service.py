from __future__ import annotations

import time
from typing import Any

from elasticsearch import Elasticsearch, helpers


class ElasticsearchService:
    """Index and search document chunks in Elasticsearch."""

    def __init__(self, url: str, index_name: str) -> None:
        self.client = Elasticsearch(url, request_timeout=30)
        self.index_name = index_name

    def ensure_index(self, max_attempts: int = 30, delay_seconds: float = 2.0) -> None:
        """Create a Russian-language full-text index if it does not exist."""
        last_error: Exception | None = None
        for _ in range(max_attempts):
            try:
                if self.client.indices.exists(index=self.index_name):
                    return
                self.client.indices.create(
                    index=self.index_name,
                    settings={
                        "analysis": {
                            "filter": {
                                "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                                "russian_stemmer": {"type": "stemmer", "language": "russian"},
                            },
                            "analyzer": {
                                "analysis_ru": {
                                    "tokenizer": "standard",
                                    "filter": ["lowercase", "russian_stop", "russian_stemmer"],
                                }
                            },
                        }
                    },
                    mappings={
                        "properties": {
                            "document_id": {"type": "keyword"},
                            "chunk_id": {"type": "keyword"},
                            "file_name": {"type": "keyword"},
                            "page_number": {"type": "integer"},
                            "text": {"type": "text", "analyzer": "analysis_ru"},
                        }
                    },
                )
                return
            except Exception as exc:  # pragma: no cover - startup retry in Docker
                last_error = exc
                time.sleep(delay_seconds)
        raise RuntimeError("Elasticsearch did not become ready") from last_error

    def index_chunks(self, chunks: list[dict[str, Any]]) -> None:
        """Bulk-index prepared chunks and refresh the index for immediate search."""
        actions = [
            {
                "_op_type": "index",
                "_index": self.index_name,
                "_id": chunk["chunk_id"],
                "_source": chunk,
            }
            for chunk in chunks
        ]
        helpers.bulk(self.client, actions)
        self.client.indices.refresh(index=self.index_name)

    def search(self, query: str, page: int, size: int) -> dict[str, Any]:
        """Run a paginated multi-match query and return normalized result items."""
        response = self.client.search(
            index=self.index_name,
            from_=(page - 1) * size,
            size=size,
            track_total_hits=True,
            query={
                "multi_match": {
                    "query": query,
                    "fields": ["text"],
                    "type": "best_fields",
                    "operator": "or",
                    "fuzziness": "AUTO",
                }
            },
            highlight={
                "pre_tags": ["[[HIGHLIGHT]]"],
                "post_tags": ["[[/HIGHLIGHT]]"],
                "fields": {"text": {"fragment_size": 500, "number_of_fragments": 1}},
            },
        )

        hits = response["hits"]["hits"]
        total = int(response["hits"]["total"]["value"])
        items = []
        for hit in hits:
            source = hit["_source"]
            highlighted = (hit.get("highlight") or {}).get("text", [None])[0]
            items.append(
                {
                    "chunk_id": source["chunk_id"],
                    "document_id": source["document_id"],
                    "file_name": source["file_name"],
                    "page": int(source.get("page_number") or 1),
                    "text": source["text"],
                    "highlight": highlighted,
                    "score": float(hit.get("_score") or 0.0),
                }
            )
        return {"total": total, "items": items}

    def ping(self) -> bool:
        """Return whether Elasticsearch is reachable."""
        return bool(self.client.ping())
