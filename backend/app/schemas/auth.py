import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

USERNAME_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё0-9_.-]+$")


class LoginRequest(BaseModel):
    """Credentials submitted by an existing user."""

    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class RegisterRequest(BaseModel):
    """Data required to create a new account."""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=200)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 3:
            raise ValueError("Логин должен содержать минимум 3 символа")
        if not USERNAME_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Логин может содержать только буквы, цифры, точку, дефис и подчёркивание"
            )
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value.isspace():
            raise ValueError("Пароль не может состоять только из пробелов")
        return value


class TokenResponse(BaseModel):
    """Bearer token returned after registration or successful login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    username: str


class CurrentUserResponse(BaseModel):
    """Current authenticated user."""

    username: str


class RegisteredUserResponse(BaseModel):
    """Public registration result without password data."""

    username: str
    created_at: datetime
