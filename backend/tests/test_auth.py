import time

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.auth import login, register
from app.api.dependencies import require_user
from app.models.database import Base
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService, InvalidTokenError


def make_service(ttl: int = 3600) -> AuthService:
    return AuthService(
        secret_key="test-secret",
        token_ttl_seconds=ttl,
        password_iterations=1_000,
    )


@pytest.fixture
def db() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_password_hash_round_trip() -> None:
    service = make_service()
    encoded_hash = service.hash_password("practice2026")
    assert encoded_hash != "practice2026"
    assert service.password_is_valid("practice2026", encoded_hash) is True
    assert service.password_is_valid("wrong", encoded_hash) is False


def test_password_hash_uses_random_salt() -> None:
    service = make_service()
    assert service.hash_password("same-password") != service.hash_password("same-password")


def test_registration_creates_user_and_returns_token(db: Session) -> None:
    service = make_service()
    response = register(
        RegisterRequest(username="NewStudent", password="strong-pass-2026"),
        db,
        service,
    )

    user = db.query(User).one()
    assert user.username == "NewStudent"
    assert user.username_key == "newstudent"
    assert user.password_hash != "strong-pass-2026"
    assert service.verify_access_token(response.access_token) == "NewStudent"


def test_registration_rejects_duplicate_username_case_insensitively(db: Session) -> None:
    service = make_service()
    register(RegisterRequest(username="Student", password="strong-pass-2026"), db, service)

    with pytest.raises(HTTPException) as error:
        register(RegisterRequest(username="student", password="another-pass-2026"), db, service)

    assert error.value.status_code == 409


def test_login_accepts_registered_user_case_insensitively(db: Session) -> None:
    service = make_service()
    register(RegisterRequest(username="Student", password="strong-pass-2026"), db, service)

    response = login(LoginRequest(username="STUDENT", password="strong-pass-2026"), db, service)

    assert response.username == "Student"
    assert service.verify_access_token(response.access_token) == "Student"


def test_login_rejects_wrong_password(db: Session) -> None:
    service = make_service()
    register(RegisterRequest(username="Student", password="strong-pass-2026"), db, service)

    with pytest.raises(HTTPException) as error:
        login(LoginRequest(username="Student", password="wrong"), db, service)

    assert error.value.status_code == 401


def test_token_round_trip() -> None:
    service = make_service()
    token = service.create_access_token("student")
    assert service.verify_access_token(token) == "student"


def test_modified_token_is_rejected() -> None:
    service = make_service()
    token = service.create_access_token("student")
    payload, signature = token.split(".", maxsplit=1)
    modified = f"{payload}x.{signature}"
    with pytest.raises(InvalidTokenError):
        service.verify_access_token(modified)


def test_expired_token_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    service = make_service(ttl=1)
    token = service.create_access_token("student")
    current_time = time.time()
    monkeypatch.setattr(time, "time", lambda: current_time + 2)
    with pytest.raises(InvalidTokenError, match="истёк"):
        service.verify_access_token(token)


def test_require_user_returns_username() -> None:
    service = make_service()
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=service.create_access_token("student"),
    )
    assert require_user(credentials, service) == "student"


def test_require_user_rejects_missing_token() -> None:
    with pytest.raises(HTTPException) as error:
        require_user(None, make_service())
    assert error.value.status_code == 401
