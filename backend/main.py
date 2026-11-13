import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import OLLAMA_URL, CHAT_MODEL

app = FastAPI(title="People's Guide API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/llm")
async def health_llm():
    """Checks whether Ollama is running and which models are installed."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            r.raise_for_status()
            models = [m["name"] for m in r.json().get("models", [])]
        return {"ollama": "running", "models": models}
    except Exception:
        return {"ollama": "not reachable", "models": []}


@app.post("/chat")
async def chat(req: ChatRequest):
    payload = {
        "model": CHAT_MODEL,
        "messages": [{"role": "user", "content": req.message}],
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            r.raise_for_status()
            return {"reply": r.json()["message"]["content"]}
    except httpx.ConnectError:
        raise HTTPException(503, "Ollama is not running or not installed yet.")
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")