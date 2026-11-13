"""Quick end-to-end check that Ollama + models work.

    python scripts/check_ollama.py
"""
import asyncio

import _path  # noqa: F401
from backend import llm


async def main():
    h = await llm.health()
    print("Ollama:", h)
    if not h.get("ok"):
        return
    print("Chat test ->", (await llm.chat("Reply in 5 words.", "Say hello to Sheffield."))[:200])
    print("JSON test ->", await llm.chat_json("Reply with JSON {\"ok\": true}", "test"))
    print("Embed test -> dims:", len((await llm.embed(["hello"]))[0]))


if __name__ == "__main__":
    asyncio.run(main())
