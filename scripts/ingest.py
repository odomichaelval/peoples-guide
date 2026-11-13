"""Build the local RAG index from data/sources/**/*.md.

    python scripts/ingest.py
"""
import asyncio

import _path  # noqa: F401
from backend.rag.store import store


async def main():
    info = await store.build()
    print(f"Indexed {info['chunks']} chunks (embeddings: {'yes' if info['embedded'] else 'NO - keyword only'})")
    for hit in await store.search("lost my job struggling to pay rent Sheffield", k=3):
        print(f"  {hit['score']:.3f}  {hit['title']}")


if __name__ == "__main__":
    asyncio.run(main())
