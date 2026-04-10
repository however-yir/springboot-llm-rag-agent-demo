#!/usr/bin/env bash
set -euo pipefail

ollama pull qwen2.5:7b
ollama pull nomic-embed-text

echo "Models are ready."
