from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import auth, documents, health, search
from app.core.config import get_settings
from app.models.database import init_db

from app.services.elasticsearch_service import ElasticsearchService
from app.services.redis_service import RedisCache

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize stateful services when the application starts."""
    init_db()
    elasticsearch = ElasticsearchService(settings.elasticsearch_url, settings.elasticsearch_index)
    elasticsearch.ensure_index()
    app.state.elasticsearch = elasticsearch
    app.state.cache = RedisCache(settings.redis_url, settings.redis_ttl_seconds)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.2.0",
    description="Поиск по внутренней базе знаний университета",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(documents.router, prefix=settings.api_prefix)
app.include_router(search.router, prefix=settings.api_prefix)
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
