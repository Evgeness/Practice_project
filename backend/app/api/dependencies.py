from fastapi import Depends, HTTPException, Request, status

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings

from app.services.auth_service import AuthService, InvalidTokenError

from app.services.elasticsearch_service import ElasticsearchService

from app.services.redis_service import RedisCache

bearer_scheme = HTTPBearer(auto_error=False)


def get_elasticsearch(request: Request) -> ElasticsearchService:
    """Return the Elasticsearch service stored on the FastAPI application."""
    return request.app.state.elasticsearch


def get_cache(request: Request) -> RedisCache:
    """Return the Redis cache stored on the FastAPI application."""
    return request.app.state.cache


def get_auth_service(settings: Settings = Depends(get_settings)) -> AuthService:
    """Build the stateless password/token service from environment settings."""
    return AuthService(
        secret_key=settings.auth_secret_key,
        token_ttl_seconds=settings.auth_token_ttl_minutes * 60,
    )


def require_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> str:
    """Require a valid Bearer token and return the authenticated username."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return auth_service.verify_access_token(credentials.credentials)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
