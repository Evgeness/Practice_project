from time import perf_counter

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_cache, get_elasticsearch, require_user
from app.models.database import get_db
from app.models.search_history import SearchHistory
from app.schemas.search import SearchHistoryItem, SearchResponse
from app.services.elasticsearch_service import ElasticsearchService
from app.services.metrics import SEARCH_DURATION, SEARCH_REQUESTS
from app.services.redis_service import RedisCache

router = APIRouter(tags=["search"])


def _save_history(db: Session, query: str, results_count: int) -> None:
    db.add(SearchHistory(query=query, results_count=results_count))
    db.commit()


@router.get("/search", response_model=SearchResponse)
def search_documents(
    q: str = Query(min_length=1, max_length=200),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    elasticsearch: ElasticsearchService = Depends(get_elasticsearch),
    cache: RedisCache = Depends(get_cache),
    _username: str = Depends(require_user),
) -> SearchResponse:
    """Search indexed chunks, cache responses for five minutes and store history."""
    query = " ".join(q.split())
    key = cache.search_key(query, page, size)
    cached = cache.get_json(key)
    if cached is not None:
        cached["cached"] = True
        SEARCH_REQUESTS.labels(cache="hit").inc()
        _save_history(db, query, int(cached.get("total", 0)))
        return SearchResponse.model_validate(cached)

    started = perf_counter()
    result = elasticsearch.search(query, page, size)
    SEARCH_DURATION.observe(perf_counter() - started)
    SEARCH_REQUESTS.labels(cache="miss").inc()

    payload = {
        "query": query,
        "page": page,
        "size": size,
        "total": result["total"],
        "cached": False,
        "items": result["items"],
    }
    cache.set_json(key, payload)
    _save_history(db, query, int(result["total"]))
    return SearchResponse.model_validate(payload)


@router.get("/search/history", response_model=list[SearchHistoryItem])
def search_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _username: str = Depends(require_user),
) -> list[SearchHistory]:
    """Return recent search queries for the prototype user."""
    statement = select(SearchHistory).order_by(SearchHistory.created_at.desc()).limit(limit)
    return list(db.scalars(statement))
