#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-http://localhost:8000}"
USERS="${USERS:-50}"
SPAWN_RATE="${SPAWN_RATE:-5}"
RUN_TIME="${RUN_TIME:-2m}"
RESULT_DIR="${RESULT_DIR:-docs/test-results}"

mkdir -p "$RESULT_DIR"
locust -f load-tests/locustfile.py \
  --headless \
  --host "$HOST" \
  --users "$USERS" \
  --spawn-rate "$SPAWN_RATE" \
  --run-time "$RUN_TIME" \
  --csv "$RESULT_DIR/load-test" \
  --html "$RESULT_DIR/load-test.html"
