import httpx
import chromadb

from backend.config import OLLAMA_URL, EMBED_MODEL

_collection = chromadb.PersistentClient(path="data/chroma").get_collection("public_services")


def search(query: str, k: int = 4):
    vec = httpx.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": [query]},
        timeout=60,
    ).json()["embeddings"]
    res = _collection.query(query_embeddings=vec, n_results=k)
    return [
        {"source": m["source"], "text": d}
        for d, m in zip(res["documents"][0], res["metadatas"][0])
    ]