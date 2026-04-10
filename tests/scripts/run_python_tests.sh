#!/usr/bin/env bash
set -euo pipefail

mkdir -p tests/coverage/python
if PYTHONPATH=ai-service python3 - <<'PY'
import importlib.util
import sys
sys.exit(0 if importlib.util.find_spec("pytest_cov") else 1)
PY
then
  PYTHONPATH=ai-service python3 -m pytest tests/python \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=xml:tests/coverage/python/coverage.xml \
    --cov-report=html:tests/coverage/python/html
else
  echo "[WARN] pytest-cov not installed, running tests without coverage reports."
  PYTHONPATH=ai-service python3 -m pytest tests/python
fi
