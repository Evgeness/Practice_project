#!/usr/bin/env bash
set -euo pipefail

RESULT_DIR="${RESULT_DIR:-docs/test-results}"
mkdir -p "$RESULT_DIR"
python scripts/evaluate_precision.py \
  --cases docs/precision_cases.example.json \
  | tee "$RESULT_DIR/precision-at-3.json"
