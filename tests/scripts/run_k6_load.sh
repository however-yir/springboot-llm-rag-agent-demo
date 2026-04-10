#!/usr/bin/env bash
set -euo pipefail

mkdir -p tests/coverage
docker run --rm -i \
  -e BASE_URL="${BASE_URL:-http://localhost/api/java}" \
  -e JWT_TOKEN="${JWT_TOKEN:-}" \
  -e VUS="${VUS:-20}" \
  -e DURATION="${DURATION:-30s}" \
  grafana/k6 run - < tests/k6/chat-load.js | tee tests/coverage/k6-summary.txt
