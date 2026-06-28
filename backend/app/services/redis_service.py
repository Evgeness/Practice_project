import hashlib
import json
from typing import Any

from redis import Redis
from redis.exceptions import RedisError


class RedisCache:
    """Small JSON cache wrapper that degrades gracefully when Redis is unavailable."""

    def __init__(self, url: str, ttl_seconds: int = 300) -> None:
        self.client = Redis.from_url(url, decode_responses=True, socket_connect_timeout=2)
        self.ttl_seconds = ttl_seconds

    @staticmethod
    def search_key(query: str, page: int, size: int) -> str:
        """Create a stable cache key for a normalized search request."""
        payload = f"{query.strip().lower()}|{page}|{size}".encode()
        return "search:" + hashlib.sha256(payload).hexdigest()

    def get_json(self, key: str) -> dict[str, Any] | None:
        """Read and decode a JSON object or return None on cache miss/error."""
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except (RedisError, json.JSONDecodeError):
            return None

    def set_json(self, key: str, value: dict[str, Any]) -> None:
        """Store a JSON object with the configured TTL."""
        try:
            self.client.setex(key, self.ttl_seconds, json.dumps(value, ensure_ascii=False))
        except RedisError:
            return

    def ping(self) -> bool:
        """Return whether Redis is reachable."""
        try:
            return bool(self.client.ping())
        except RedisError:
            return False
