import httpx
import chromadb
from bs4 import BeautifulSoup

from backend.config import OLLAMA_URL, EMBED_MODEL

PAGES = [
    "https://www.gov.uk/council-tax-reduction",
    "https://www.gov.uk/housing-benefit",
    "https://www.gov.uk/universal-credit",
    "https://www.gov.uk/jobseekers-allowance",
    "https://www.sheffield.gov.uk/benefits/apply-benefits-support/council-tax-support",
    "https://www.sheffield.gov.uk/benefits/apply-benefits-support/discretionary-CRFHP",
    "https://www.sheffield.gov.uk/benefits/apply-benefits-support/local-assistance-scheme",
]

client = chromadb.PersistentClient(path="data/chroma")
collection = client.get_or_create_collection("public_services")


def fetch_text(url: str) -> str:
    r = httpx.get(url, timeout=30, follow_redirects=True)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    main = soup.find("main") or soup
    for tag in main(["script", "style", "nav", "footer"]):
        tag.decompose()
    return " ".join(main.get_text(" ").split())


def chunk(text: str, size: int = 900, overlap: int = 150):
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step) if text[i:i + size].strip()]


def embed(texts):
    r = httpx.post(f"{OLLAMA_URL}/api/embed",
                   json={"model": EMBED_MODEL, "input": texts}, timeout=120)
    r.raise_for_status()
    return r.json()["embeddings"]


def main():
    for url in PAGES:
        try:
            text = fetch_text(url)
        except Exception as e:
            print(f"SKIP {url}: {e}")
            continue
        chunks = chunk(text)
        vectors = embed(chunks)
        collection.upsert(
            ids=[f"{url}#{i}" for i in range(len(chunks))],
            documents=chunks,
            embeddings=vectors,
            metadatas=[{"source": url}] * len(chunks),
        )
        print(f"OK   {url}: {len(chunks)} chunks")
    print("Total chunks stored:", collection.count())


if __name__ == "__main__":
    main()