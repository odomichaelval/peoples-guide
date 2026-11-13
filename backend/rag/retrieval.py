import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_FILE = PROJECT_ROOT / "data" / "sources" / "official_pages.json"

STOP_WORDS = {
    "the", "and", "for", "with", "that", "this", "have",
    "are", "was", "you", "your", "from", "can", "but",
    "not", "what", "how", "any", "been",
}


def tokens(text):
    return {
        word
        for word in re.findall(r"[a-z]+", text.lower())
        if len(word) > 2 and word not in STOP_WORDS
    }


def retrieve(query, limit=4):
    pages = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    query_tokens = tokens(query)
    matches = []

    for page in pages:
        words = page["text"].split()

        for start in range(0, len(words), 180):
            passage = " ".join(words[max(0, start - 100):start + 340])

            if not passage:
                continue

            passage_tokens = tokens(passage)
            title_tokens = tokens(page["title"])

            score = (
                len(query_tokens & passage_tokens)
                + 2 * len(query_tokens & title_tokens)
            )

            if score:
                matches.append({
                    "passage_id": f"{page['source_id']}-{start}",
                    "title": page["title"],
                    "url": page["url"],
                    "retrieved_at": page["retrieved_at"],
                    "text": passage,
                    "score": score,
                })

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:limit]