import base64
import binascii
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass


class InvalidTokenError(ValueError):
    """Raised when an access token is malformed, expired or has a bad signature."""


@dataclass(frozen=True)
class AuthService:
    """Password hashing and compact HMAC-signed access tokens."""

    secret_key: str
    token_ttl_seconds: int
    password_iterations: int = 310_000

    @staticmethod
    def _b64encode(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    @staticmethod
    def _b64decode(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)

    @staticmethod
    def normalize_username(username: str) -> str:
        """Return a stable case-insensitive key for username lookup."""
        return username.strip().casefold()

    def hash_password(self, password: str) -> str:
        """Hash a password with PBKDF2-SHA256 and a random per-user salt."""
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self.password_iterations,
        )
        return (
            f"pbkdf2_sha256${self.password_iterations}$"
            f"{self._b64encode(salt)}${self._b64encode(digest)}"
        )

    def password_is_valid(self, password: str, encoded_hash: str) -> bool:
        """Verify a submitted password against a stored PBKDF2 hash."""
        try:
            algorithm, iterations_text, encoded_salt, encoded_digest = encoded_hash.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            iterations = int(iterations_text)
            salt = self._b64decode(encoded_salt)
            expected_digest = self._b64decode(encoded_digest)
            supplied_digest = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                iterations,
            )
            return hmac.compare_digest(supplied_digest, expected_digest)
        except (ValueError, TypeError, binascii.Error):
            return False

    def create_access_token(self, username: str) -> str:
        """Create a compact signed token containing username and expiration time."""
        payload = {
            "sub": username,
            "exp": int(time.time()) + self.token_ttl_seconds,
        }
        encoded_payload = self._b64encode(
            json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        )
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            encoded_payload.encode("ascii"),
            hashlib.sha256,
        ).digest()
        return f"{encoded_payload}.{self._b64encode(signature)}"

    def verify_access_token(self, token: str) -> str:
        """Validate a token and return the authenticated username."""
        try:
            encoded_payload, encoded_signature = token.split(".", maxsplit=1)
            supplied_signature = self._b64decode(encoded_signature)
            expected_signature = hmac.new(
                self.secret_key.encode("utf-8"),
                encoded_payload.encode("ascii"),
                hashlib.sha256,
            ).digest()
            if not hmac.compare_digest(supplied_signature, expected_signature):
                raise InvalidTokenError("Некорректная подпись токена")

            payload = json.loads(self._b64decode(encoded_payload).decode("utf-8"))
            username = payload.get("sub")
            expires_at = int(payload.get("exp", 0))
            if not isinstance(username, str) or not username.strip():
                raise InvalidTokenError("В токене отсутствует пользователь")
            if expires_at <= int(time.time()):
                raise InvalidTokenError("Срок действия токена истёк")
            return username
        except (
            ValueError,
            TypeError,
            binascii.Error,
            json.JSONDecodeError,
            UnicodeDecodeError,
        ) as exc:
            if isinstance(exc, InvalidTokenError):
                raise
            raise InvalidTokenError("Некорректный токен") from exc
