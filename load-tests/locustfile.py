import os

from locust import HttpUser, between, task


class SearchUser(HttpUser):
    """Simulate authenticated users repeatedly querying the search endpoint."""

    wait_time = between(0.5, 2.0)

    queries = [
        "университет",
        "программная инженерия",
        "поиск документов",
        "Elasticsearch",
        "учебная практика",
    ]

    def on_start(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": os.getenv("AUTH_USERNAME", "student"),
                "password": os.getenv("AUTH_PASSWORD", "practice2026"),
            },
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]

    @task
    def search(self) -> None:
        query = self.queries[hash(self.environment.runner.user_count) % len(self.queries)]
        self.client.get(
            "/api/v1/search",
            params={"q": query, "page": 1, "size": 10},
            headers={"Authorization": f"Bearer {self.token}"},
        )
