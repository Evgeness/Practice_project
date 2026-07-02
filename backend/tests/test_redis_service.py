from app.services.redis_service import RedisCache


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def get(self, key: str):
        return self.values.get(key)

    def setex(self, key: str, ttl: int, value: str) -> None:
        assert ttl == 300
        self.values[key] = value

    def ping(self) -> bool:
        return True


def test_cache_round_trip_and_key_normalization() -> None:
    cache = RedisCache("redis://unused")
    cache.client = FakeRedis()
    key1 = cache.search_key("  Elasticsearch ", 1, 10)
    key2 = cache.search_key("elasticsearch", 1, 10)
    assert key1 == key2

    cache.set_json(key1, {"total": 3, "items": []})
    assert cache.get_json(key1) == {"total": 3, "items": []}
    assert cache.ping() is True