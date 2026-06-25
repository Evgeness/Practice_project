from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_cache, get_elasticsearch
from app.models.database import get_db
from app.services.elasticsearch_service import ElasticsearchService
from app.services.redis_service import RedisCache

router = APIRouter(tags=["system"])


@router.get("/health")
def health(
    db: Session = Depends(get_db),
    elasticsearch: ElasticsearchService = Depends(get_elasticsearch),
    cache: RedisCache = Depends(get_cache),
) -> dict[str, object]:
    """Report readiness of the API and its dependencies."""
    database_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        database_ok = False

    services = {
        "database": database_ok,
        "elasticsearch": elasticsearch.ping(),
        "redis": cache.ping(),
    }
    return {"status": "ok" if all(services.values()) else "degraded", "services": services}
