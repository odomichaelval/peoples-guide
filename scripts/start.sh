#!/usr/bin/env bash
# Production-style: FastAPI serves the API *and* the built React app on one port.
#   bash scripts/start.sh      ->  http://localhost:8000  (forward port 8000 in VS Code)
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; [ -f .env ] && source .env; set +a
curl -sf "${OLLAMA_HOST:-http://127.0.0.1:11434}/api/tags" >/dev/null || (nohup ollama serve > /tmp/ollama.log 2>&1 &)
exec uvicorn backend.main:app --host 0.0.0.0 --port "${API_PORT:-8000}"
