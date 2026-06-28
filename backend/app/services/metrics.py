from prometheus_client import Counter, Histogram

SEARCH_REQUESTS = Counter(
    "knowledge_search_requests_total",
    "Number of requests made to the search endpoint",
    ["cache"],
)
SEARCH_DURATION = Histogram(
    "knowledge_search_duration_seconds",
    "Time spent processing a search request",
)
