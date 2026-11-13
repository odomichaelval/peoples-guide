import json
import traceback

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from backend import auth, llm
from backend.agents.graph import AGENTS, guide_graph
from backend.app.schemas import GuideIn
from backend.rag.store import store

router = APIRouter(prefix="/api", tags=["guide"])
AGENT_NAMES = {k: name for k, name, _ in AGENTS}
ORDER = [k for k, _, _ in AGENTS]


def sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@router.get("/health")
async def health():
    return {"api": "ok", "ollama": await llm.health(),
            "index": {"chunks": len(store.chunks), "embedded": store.vectors is not None}}


@router.get("/agents")
def agents():
    return [{"key": k, "name": n} for k, n, _ in AGENTS]


@router.post("/guide/stream")
async def guide_stream(body: GuideIn, user=Depends(auth.current_user)):
    """Runs the multi-agent pipeline and streams each agent's result (Server-Sent Events)."""

    async def gen():
        state = {"query": body.query, "location": body.location, "trace": []}
        yield sse("agent_start", {"agent": ORDER[0], "name": AGENT_NAMES[ORDER[0]]})
        try:
            async for update in guide_graph.astream(state, stream_mode="updates"):
                for node, out in update.items():
                    out = out or {}
                    yield sse("agent_done", {"agent": node, "name": AGENT_NAMES.get(node, node),
                                             "trace": (out.get("trace") or [{}])[-1],
                                             "output": {k: v for k, v in out.items() if k != "trace"}})
                    i = ORDER.index(node) if node in ORDER else -1
                    if 0 <= i < len(ORDER) - 1:
                        nxt = ORDER[i + 1]
                        yield sse("agent_start", {"agent": nxt, "name": AGENT_NAMES[nxt]})
            yield sse("done", {"ok": True})
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            yield sse("error", {"message": str(e)})

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.post("/guide/run")
async def guide_run(body: GuideIn, user=Depends(auth.current_user)):
    """Non-streaming version (handy for testing with curl / Swagger)."""
    return await guide_graph.ainvoke({"query": body.query, "location": body.location, "trace": []})


@router.get("/rag/search")
async def rag_search(q: str, k: int = 5, user=Depends(auth.current_user)):
    return await store.search(q, k)


@router.post("/rag/rebuild")
async def rag_rebuild(user=Depends(auth.current_user)):
    return await store.build()


@router.get("/sources")
def sources(user=Depends(auth.current_user)):
    seen = {}
    for c in store.chunks:
        seen.setdefault(c.url, {"title": c.title, "url": c.url, "provider": c.provider, "category": c.category})
    return sorted(seen.values(), key=lambda s: (s["category"], s["title"]))
