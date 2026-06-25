import time
from collections.abc import Generator

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def ensure_default_user() -> None:
    """Create the optional demonstration account when it does not exist yet."""
    from app.models.user import User
    from app.services.auth_service import AuthService

    username = settings.auth_username.strip()
    password = settings.auth_password
    if not username or not password:
        return

    auth_service = AuthService(
        secret_key=settings.auth_secret_key,
        token_ttl_seconds=settings.auth_token_ttl_minutes * 60,
    )
    username_key = auth_service.normalize_username(username)
    with SessionLocal() as session:
        existing_user = session.scalar(select(User).where(User.username_key == username_key))
        if existing_user is not None:
            return
        session.add(
            User(
                username=username,
                username_key=username_key,
                password_hash=auth_service.hash_password(password),
            )
        )
        session.commit()


def init_db(max_attempts: int = 30, delay_seconds: float = 2.0) -> None:
    """Create database tables and seed the demo account while PostgreSQL starts."""
    # Import models so SQLAlchemy knows their metadata.
    from app.models import document, search_history, user  # noqa: F401

    last_error: Exception | None = None
    for _ in range(max_attempts):
        try:
            Base.metadata.create_all(bind=engine)
            ensure_default_user()
            return
        except Exception as exc:  # pragma: no cover - exercised in Docker startup
            last_error = exc
            time.sleep(delay_seconds)
    raise RuntimeError("Database did not become ready") from last_error


def get_db() -> Generator[Session, None, None]:
    """Provide a database session to a request and always close it."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
