"""Agent 2 - Research: retrieves evidence from the local index of trusted public sources."""
import time

from backend.agents.state import GuideState
from backend.rag.store import store


async def research_agent(state: GuideState) -> GuideState:
    t = time.time()
    needs = state.get("needs", {})
    queries = list(needs.get("search_queries", []))
    queries += [f"{n.get('category', '')} {n.get('description', '')}" for n in needs.get("needs", [])]
    location = state.get("location") or "Sheffield"
    queries = [f"{q} {location}" for q in queries if q.strip()] or [state["query"]]

    best: dict[str, dict] = {}
    for q in queries[:12]:
        for hit in await store.search(q, k=6):
            if hit["id"] not in best or hit["score"] > best[hit["id"]]["score"]:
                best[hit["id"]] = hit

    # Keep the top chunks, max 2 per source page so we cover more services.
    per_url: dict[str, int] = {}
    evidence = []
    for hit in sorted(best.values(), key=lambda h: -h["score"]):
        if per_url.get(hit["url"], 0) >= 2:
            continue
        per_url[hit["url"]] = per_url.get(hit["url"], 0) + 1
        evidence.append(hit)
        if len(evidence) >= 14:
            break
    for i, e in enumerate(evidence, 1):
        e["ref"] = f"S{i}"

    return {
        "evidence": evidence,
        "trace": [{
            "agent": "research",
            "message": f"Searched {len(queries[:12])} queries, found {len(evidence)} passages from "
                       f"{len(per_url)} trusted sources",
            "seconds": round(time.time() - t, 1),
        }],
    }


def format_evidence(evidence: list[dict], max_chars: int = 900) -> str:
    return "\n\n".join(
        f"[{e['ref']}] {e['title']} ({e['provider']}) - {e['url']}\n{e['text'][:max_chars]}"
        for e in evidence
    )
