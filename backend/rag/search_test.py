import httpx
import chromadb
from backend.config import OLLAMA_URL, EMBED_MODEL

collection = chromadb.PersistentClient(path="data/chroma").get_collection("public_services")

q = "I can't afford my rent and need emergency help in Sheffieldpython -m backend.rag.search_test"
vec = httpx.post(f"{OLLAMA_URL}/api/embed",
                 json={"model": EMBED_MODEL, "input": [q]}, timeout=60).json()["embeddings"]
res = collection.query(query_embeddings=vec, n_results=3)

for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
    print(meta["source"])
    print(doc[:200], "\n")