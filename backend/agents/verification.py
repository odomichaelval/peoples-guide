"""Agent 5 - Verification: cross-checks every recommendation against trusted sources.

Two layers:
1. Deterministic - every URL must be on the trusted-domain allowlist, and every
   cited ref must exist in the retrieved evidence.
2. LLM fact check - is each step actually supported by its cited passages?
"""
import json
import time
from urllib.parse import urlparse

from backend import llm
from backend.agents.state import GuideState
from backend.config import settings

SYSTEM = """You are the Verification Agent for People's Guide. You check recommendations for misinformation.
For each step, decide whether its claims are supported by the cited evidence passages.
Return ONLY JSON:
{"checks": [{"index": 0, "supported": true/false, "note": "short reason"}],
 "overall_note": "one sentence for the resident about how reliable this plan is"}"""


def trusted_domains() -> list[str]:
    try:
        return json.loads(settings.trusted_sources_file.read_text())["trusted_domains"]
    except Exception:  # noqa: BLE001
        return ["gov.uk", "sheffield.gov.uk", "nhs.uk", "citizensadvice.org.uk"]


def is_trusted(url: str, domains: list[str]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return bool(host) and any(host == d or host.endswith("." + d) for d in domains)


async def verification_agent(state: GuideState) -> GuideState:
    t = time.time()
    plan = state.get("plan", {})
    steps = plan.get("steps", [])
    evidence = {e["ref"]: e for e in state.get("evidence", [])}
    evidence_urls = {e["url"] for e in evidence.values()}
    domains = trusted_domains()

    # Layer 1: deterministic checks
    to_llm = []
    for i, s in enumerate(steps):
        if s.get("verified") is True:  # built-in crisis step
            continue
        url = s.get("url", "")
        refs = [r for r in s.get("refs", []) if r in evidence]
        s["refs"] = refs
        problems = []
        if refs and url not in evidence_urls:
            # Prefer the URL of the evidence we actually retrieved.
            url = evidence[refs[0]]["url"]
        if url and not is_trusted(url, domains):
            problems.append("link is not on the trusted-source list")
            url = ""
        s["url"] = url
        if not refs:
            problems.append("no supporting evidence cited")
        s["verified"] = not problems
        s["verification_note"] = "; ".join(problems) if problems else "Matches a trusted source"
        s["sources"] = [{"ref": r, "title": evidence[r]["title"], "url": evidence[r]["url"]} for r in refs]
        if refs:
            to_llm.append((i, s))

    # Layer 2: LLM fact-check against cited passages
    overall = "Recommendations were checked against official sources."
    if to_llm:
        payload = [
            {"index": i, "title": s.get("title"), "why": s.get("why"), "how": s.get("how"),
             "evidence": [evidence[r]["text"][:700] for r in s["refs"]]}
            for i, s in to_llm
        ]
        try:
            out = await llm.chat_json(SYSTEM, json.dumps(payload, indent=1))
            for c in out.get("checks", []):
                idx = c.get("index")
                if isinstance(idx, int) and 0 <= idx < len(steps) and c.get("supported") is False:
                    steps[idx]["verified"] = False
                    steps[idx]["verification_note"] = c.get("note", "Not fully supported by the source")
            overall = out.get("overall_note", overall)
        except llm.LLMError:
            overall = "Automatic fact-check unavailable; links were checked against the trusted list."

    verified = sum(1 for s in steps if s.get("verified"))
    confidence = round(verified / len(steps), 2) if steps else 0.0
    return {
        "plan": plan,
        "verification": {
            "verified_steps": verified,
            "total_steps": len(steps),
            "confidence": confidence,
            "note": overall,
            "trusted_domains": domains,
        },
        "trace": [{
            "agent": "verification",
            "message": f"{verified}/{len(steps)} steps verified against trusted sources",
            "seconds": round(time.time() - t, 1),
        }],
    }
