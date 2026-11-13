"""Minimal async client for the local Ollama server (chat + embeddings)."""
import json
import re
from typing import Any

import httpx

from backend.config import settings


class LLMError(RuntimeError):
    pass


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=settings.ollama_host, timeout=settings.llm_timeout_seconds)


async def chat(system: str, user: str, json_mode: bool = False) -> str:
    payload: dict[str, Any] = {
        "model": settings.chat_model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": False,
        "think": settings.ollama_think,
        "options": {"temperature": settings.llm_temperature, "num_ctx": 16384},
    }
    if json_mode:
        payload["format"] = "json"
    async with _client() as client:
        try:
            r = await client.post("/api/chat", json=payload)
        except httpx.HTTPError as e:
            raise LLMError(f"Cannot reach Ollama at {settings.ollama_host}: {e}") from e
        if r.status_code == 400 and "think" in r.text.lower():
            # Model doesn't support the think flag - retry without it.
            payload.pop("think", None)
            r = await client.post("/api/chat", json=payload)
        if r.status_code != 200:
            raise LLMError(f"Ollama error {r.status_code}: {r.text[:300]}")
        return r.json()["message"]["content"]


def parse_json(text: str) -> Any:
    """Parse JSON from a model reply, tolerating <think> blocks and code fences."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"(\{.*\}|\[.*\])", text, flags=re.S)
        if m:
            return json.loads(m.group(1))
        raise


async def chat_json(system: str, user: str, retries: int = 1) -> Any:
    last: Exception | None = None
    for _ in range(retries + 1):
        reply = await chat(system, user, json_mode=True)
        try:
            return parse_json(reply)
        except (json.JSONDecodeError, ValueError) as e:
            last = e
            user = user + "\n\nYour last reply was not valid JSON. Reply with ONLY valid JSON."
    raise LLMError(f"Model did not return valid JSON: {last}")


async def embed(texts: list[str]) -> list[list[float]]:
    async with _client() as client:
        try:
            r = await client.post("/api/embed", json={"model": settings.embed_model, "input": texts})
        except httpx.HTTPError as e:
            raise LLMError(f"Cannot reach Ollama at {settings.ollama_host}: {e}") from e
        if r.status_code != 200:
            raise LLMError(f"Ollama embed error {r.status_code}: {r.text[:300]}")
        return r.json()["embeddings"]


async def health() -> dict:
    async with _client() as client:
        try:
            r = await client.get("/api/tags", timeout=5)
            models = [m["name"] for m in r.json().get("models", [])]
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}

    def has(name: str) -> bool:
        return any(m == name or m.startswith(name + ":") for m in models)

    return {
        "ok": True,
        "chat_model": settings.chat_model,
        "chat_model_ready": has(settings.chat_model),
        "embed_model": settings.embed_model,
        "embed_model_ready": has(settings.embed_model),
        "models": models,
    }
