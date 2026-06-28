from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SearchResultItem(BaseModel):
    """One matching text chunk returned by Elasticsearch."""

    chunk_id: str
    document_id: str
    file_name: str
    page: int
    text: str
    highlight: str | None = None
    score: float


class SearchResponse(BaseModel):
    """Paginated search response."""

    query: str
    page: int
    size: int
    total: int
    cached: bool = False
    items: list[SearchResultItem] = Field(default_factory=list)


class SearchHistoryItem(BaseModel):
    """Stored search history entry."""

    id: int
    query: str
    results_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
