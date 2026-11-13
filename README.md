# People's Guide
**The Right Support. The Right Information. One Place.**

A privacy-first, multi-agent UK public services navigator. Everything (the LLM, the embeddings and the document index) runs locally on an NVIDIA DGX Spark through Ollama. No resident data goes to a cloud AI.

```
Resident ──► React UI (login) ──► FastAPI ──► LangGraph pipeline ──► Ollama (nemotron-3-nano) on the Spark
                                               │
   1 Needs Assessment → 2 Research (local RAG) → 3 Eligibility → 4 Planning → 5 Verification
```

| Agent | What it does | File |
|---|---|---|
| Needs Assessment | Turns the resident's story into structured circumstances + needs + search queries | `backend/agents/needs.py` |
| Research | Hybrid search (vectors + keywords) over the local index of GOV.UK / Sheffield / NHS pages | `backend/agents/research.py` |
| Eligibility | Compares circumstances with published criteria; "likely / possible / unlikely" with citations | `backend/agents/eligibility.py` |
| Planning | Prioritised action plan, documents to gather; adds crisis step if safety flags | `backend/agents/planning.py` |
| Verification | Trusted-domain allowlist + citation check + LLM fact-check against cited passages | `backend/agents/verification.py` |

---

## Step-by-step setup in VS Code (Remote-SSH on spark5)

### 1. Back up what you already have
In the VS Code terminal (`Ctrl+'`) on the Spark:
```bash
cd ~/peoples-guide
git add -A && git commit -m "backup before People's Guide scaffold" || true
```

### 2. Upload and unzip
1. Drag `peoples-guide.zip` from Windows into the VS Code **Explorer** panel, into your home folder (or the `peoples-guide` folder).
2. In the terminal:
```bash
cd ~
unzip -o peoples-guide.zip -d ~        # if unzip is missing: python3 -m zipfile -e peoples-guide.zip ~
cd ~/peoples-guide
```
This overwrites `backend/auth.py`, `config.py` and `main.py` with the new versions. Your old ones are in git.

### 3. One-command install
```bash
bash scripts/setup.sh
```
This creates `.venv`, installs Python packages, creates `.env` with a random secret, installs/starts Ollama if needed, pulls `nemotron-3-nano` (~24 GB) and `nomic-embed-text`, installs Node (via nvm if missing), builds the React app, creates the demo login and builds the RAG index.

> If `python3 -m venv` fails: `sudo apt install -y python3-venv`. The Ollama installer needs sudo once.

### 4. Run it
```bash
bash scripts/start.sh
```
VS Code will pop up "Port 8000 is available". Click **Open in Browser**, or open the **Ports** tab and forward `8000`. Then go to **http://localhost:8000** on your laptop. Teammates on the same network can use **http://spark5.local:8000**.

**Login:** `demo` / `PeoplesGuide2026!` (change it in `.env` or with `python scripts/create_user.py demo 'NewPass'`). The login page also has "Create an account".

### 5. (Optional) Development mode with hot reload
```bash
bash scripts/dev.sh      # API on :8000 with auto-reload, React on :5173
```
Forward port **5173** and open http://localhost:5173.

---

## Useful commands
```bash
source .venv/bin/activate
python scripts/check_ollama.py                 # test Ollama, chat, JSON and embeddings
python scripts/fetch_sources.py                # download live GOV.UK/NHS/Sheffield pages into the index
python scripts/fetch_sources.py --url https://www.sheffield.gov.uk/<page> --category housing --provider "Sheffield City Council"
python scripts/ingest.py                       # rebuild the index after editing data/sources/
python scripts/create_user.py alice 'Pass123!' "Alice Smith"
ollama ps                                      # see loaded models / memory use
```
API docs (Swagger): http://localhost:8000/docs. Click **Authorize** and paste the token from `/api/auth/login`.

## Knowledge base
- `data/sources/seed/*.md`: hand-written summaries of key services (Universal Credit, Council Tax Support, DHP, homelessness, free school meals, Warm Home Discount, Pension Credit, PIP, NHS costs, Citizens Advice, students, jobs). They have no £ amounts on purpose. **Before the demo, run `fetch_sources.py`** so answers come from the live official pages.
- `data/sources/fetched/`: pages downloaded by `fetch_sources.py`.
- `data/trusted_sources.json`: the domain allowlist used by the Verification Agent, plus the URLs to fetch. Add Sheffield City Council page URLs here as you find them.
- To add a source, drop a `.md` file with this header into `data/sources/` and run `python scripts/ingest.py`:
```
---
title: ...
url: https://...
provider: ...
category: housing
---
text...
```

## Configuration (`.env`)
| Key | Default | Notes |
|---|---|---|
| `CHAT_MODEL` | `nemotron-3-nano` | Try `nemotron-3-super` (~87 GB) for better reasoning; slower |
| `EMBED_MODEL` | `nomic-embed-text` | |
| `OLLAMA_THINK` | `false` | `true` = Nemotron reasoning mode (slower, sometimes better) |
| `ALLOW_SIGNUP` | `true` | Set `false` to disable "Create an account" |

## Privacy notes (good for the pitch)
- LLM + embeddings + vector index are all on the Spark; the only outbound traffic is `fetch_sources.py` downloading **public** pages.
- Residents' queries are **not stored**: SQLite holds only usernames and bcrypt password hashes.
- The browser keeps the login in `sessionStorage`, so it's gone when the tab closes. No external fonts or CDNs.

## Troubleshooting
| Problem | Fix |
|---|---|
| Header says "Local AI offline" | `ollama serve &`, then `curl localhost:11434/api/tags` |
| "Model ... not pulled" | `ollama pull nemotron-3-nano` |
| Slow first answer | First call loads the model into memory (~20-40 s); later calls are fast |
| `Model did not return valid JSON` | Retry, set `LLM_TEMPERATURE=0.1`, or switch `CHAT_MODEL` |
| Port 8000 busy | `API_PORT=8001` in `.env` (and update `frontend/vite.config.js` proxy for dev mode) |
| Blank page at :8000 | `cd frontend && npm run build` |

*Guidance only. Not legal or financial advice. Service providers make the final eligibility decisions.*
