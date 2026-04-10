#!/usr/bin/env bash
set -euo pipefail

mkdir -p tests/coverage
npm --prefix tests/e2e install
npx --prefix tests/e2e playwright install --with-deps chromium
npm --prefix tests/e2e run test
