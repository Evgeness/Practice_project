#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000/api/v1}"
AUTH_USERNAME="${AUTH_USERNAME:-student}"
AUTH_PASSWORD="${AUTH_PASSWORD:-practice2026}"
DOWNLOAD_DIR="${DOWNLOAD_DIR:-./.demo-documents}"
mkdir -p "$DOWNLOAD_DIR"

URLS=(
  "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
  "https://www.africau.edu/images/default/sample.pdf"
  "https://www.orimi.com/pdf-test.pdf"
  "https://www.clickdimensions.com/links/TestPDFfile.pdf"
  "https://gahp.net/wp-content/uploads/2017/09/sample.pdf"
  "https://unec.edu.az/application/uploads/2014/12/pdf-sample.pdf"
  "https://www.princexml.com/samples/invoice/invoicesample.pdf"
  "https://www.princexml.com/howcome/2016/samples/magic.pdf"
  "https://www.cs.cmu.edu/~pausch/Randy/Randy/pauschlastlecturetranscript.pdf"
  "https://arxiv.org/pdf/1706.03762"
)

echo "Waiting for API at $API_URL/health ..."
until curl -fsS "$API_URL/health" >/dev/null; do
  sleep 3
done

echo "Logging in as $AUTH_USERNAME ..."
TOKEN="$({ curl -fsS -X POST "$API_URL/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"$AUTH_USERNAME\",\"password\":\"$AUTH_PASSWORD\"}"; } \
  | python -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')"

index=0
for url in "${URLS[@]}"; do
  index=$((index + 1))
  file="$DOWNLOAD_DIR/document-$index.pdf"
  echo "[$index/${#URLS[@]}] Downloading $url"
  if curl -fL --retry 2 --connect-timeout 10 "$url" -o "$file"; then
    echo "Uploading $file"
    curl -fsS -X POST "$API_URL/documents/upload" \
      -H "Authorization: Bearer $TOKEN" \
      -F "file=@$file" >/dev/null || true
  else
    echo "Skipped unavailable URL: $url" >&2
  fi
done

echo "Initialization finished. Open http://localhost:3000"
