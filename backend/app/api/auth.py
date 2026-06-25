from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_auth_service, require_user
from app.models.database import get_db
from app.models.user import User
from app.schemas.auth import CurrentUserResponse, LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def build_token_response(auth_service: AuthService, username: str) -> TokenResponse:
    """Build a common token response for login and registration."""
    return TokenResponse(
        access_token=auth_service.create_access_token(username),
        expires_in=auth_service.token_ttl_seconds,
        username=username,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    registration: RegisterRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Create a user account and immediately issue an access token."""
    username = registration.username.strip()
    username_key = auth_service.normalize_username(username)

    existing_user = db.scalar(select(User).where(User.username_key == username_key))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким логином уже существует",
        )

    user = User(
        username=username,
        username_key=username_key,
        password_hash=auth_service.hash_password(registration.password),
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким логином уже существует",
        ) from exc

    return build_token_response(auth_service, user.username)


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate a registered user and issue a bearer token."""
    username_key = auth_service.normalize_username(credentials.username)
    user = db.scalar(select(User).where(User.username_key == username_key))
    if user is None or not auth_service.password_is_valid(
        credentials.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return build_token_response(auth_service, user.username)


@router.get("/me", response_model=CurrentUserResponse)
def current_user(username: str = Depends(require_user)) -> CurrentUserResponse:
    """Return the username encoded in the current valid access token."""
    return CurrentUserResponse(username=username)
