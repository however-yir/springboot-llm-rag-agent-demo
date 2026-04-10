#!/usr/bin/env bash
set -euo pipefail

mkdir -p tests/coverage/java
(cd backend-java && mvn -q test)
