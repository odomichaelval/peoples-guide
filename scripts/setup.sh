#!/usr/bin/env bash
# One-shot setup for People's Guide on the DGX Spark.
#   bash scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)
say() { printf "\n\033[1;32m==> %s\033[0m\n" "$*"; }

say "1/6 Checking system tools"
command -v python3 >/dev/null || { echo "python3 missing"; exit 1; }
python3 -c 'import venv' 2>/dev/null || { echo "Run: sudo apt install -y python3-venv"; exit 1; }

say "2/6 Python virtual environment (.venv)"
[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt

say "3/6 .env configuration"
if [ ! -f .env ]; then
  cp .env.example .env
  SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
  sed -i "s/^JWT_SECRET=.*/JWT_SECRET=$SECRET/" .env
  echo "Created .env with a random JWT secret"
fi
set -a; source .env; set +a

say "4/6 Ollama + models (runs 100% locally)"
if ! command -v ollama >/dev/null; then
  echo "Installing Ollama (needs sudo)..."
  curl -fsSL https://ollama.com/install.sh | sh
fi
if ! curl -sf "${OLLAMA_HOST:-http://127.0.0.1:11434}/api/tags" >/dev/null; then
  echo "Starting ollama serve in background..."
  (nohup ollama serve > /tmp/ollama.log 2>&1 &) ; sleep 4
fi
ollama pull "${CHAT_MODEL:-nemotron-3-nano}"
ollama pull "${EMBED_MODEL:-nomic-embed-text}"

say "5/6 Frontend (React + Vite)"
if ! command -v npm >/dev/null; then
  echo "Node.js not found - installing Node 20 via nvm (no sudo needed)..."
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] || curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  # shellcheck disable=SC1091
  source "$NVM_DIR/nvm.sh"; nvm install 20
fi
(cd frontend && npm install && npm run build)

say "6/6 Database, demo login and RAG index"
python scripts/create_user.py "${DEMO_USERNAME:-demo}" "${DEMO_PASSWORD:-PeoplesGuide2026!}" "Demo User"
python scripts/ingest.py

say "Done! Start the app with:  bash scripts/start.sh"
echo "Login: ${DEMO_USERNAME:-demo} / ${DEMO_PASSWORD:-PeoplesGuide2026!}"
