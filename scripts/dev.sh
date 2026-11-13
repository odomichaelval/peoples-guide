#!/usr/bin/env bash
# Development: backend with auto-reload on :8000 + Vite hot-reload frontend on :5173.
#   bash scripts/dev.sh        ->  open http://localhost:5173
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
set -a; [ -f .env ] && source .env; set +a
[ -s "$HOME/.nvm/nvm.sh" ] && source "$HOME/.nvm/nvm.sh"
curl -sf "${OLLAMA_HOST:-http://127.0.0.1:11434}/api/tags" >/dev/null || (nohup ollama serve > /tmp/ollama.log 2>&1 &)
uvicorn backend.main:app --host 0.0.0.0 --port "${API_PORT:-8000}" --reload --reload-dir backend &
API_PID=$!
trap 'kill $API_PID 2>/dev/null' EXIT
cd frontend && npm run dev
