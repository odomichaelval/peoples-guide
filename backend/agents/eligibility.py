"""Agent 3 - Eligibility: compares circumstances with published criteria."""
import json
import time

from backend import llm
from backend.agents.research import format_evidence
from backend.agents.state import GuideState

SYSTEM = """You are the Eligibility Agent for People's Guide.
Using ONLY the evidence passages provided, decide which services the resident may be eligible for.
Never claim someone definitely qualifies - only the provider can decide. If a criterion is
unknown, list it under "to_confirm". Every service MUST cite evidence refs like "S3".
Ignore services that clearly do not apply.

Return ONLY JSON:
{"services": [
  {"name": "service name", "provider": "who runs it", "url": "url from the evidence",
   "likelihood": "likely | possible | unlikely",
   "why": "plain-English reason linked to their circumstances",
   "criteria_met": ["..."], "to_confirm": ["..."],
   "refs": ["S1"]}
]}"""


async def eligibility_agent(state: GuideState) -> GuideState:
    t = time.time()
    evidence = state.get("evidence", [])
    if not evidence:
        return {"eligibility": [], "trace": [{"agent": "eligibility", "message": "No evidence to assess", "seconds": 0}]}
    user = (
        f"Resident circumstances:\n{json.dumps(state['needs'], indent=1)}\n\n"
        f"Evidence passages:\n{format_evidence(evidence)}"
    )
    out = await llm.chat_json(SYSTEM, user)
    services = out.get("services", out if isinstance(out, list) else [])
    order = {"likely": 0, "possible": 1, "unlikely": 2}
    services.sort(key=lambda s: order.get(s.get("likelihood", "possible"), 1))
    likely = sum(1 for s in services if s.get("likelihood") == "likely")
    return {
        "eligibility": services,
        "trace": [{
            "agent": "eligibility",
            "message": f"Assessed {len(services)} services ({likely} likely match)",
            "seconds": round(time.time() - t, 1),
        }],
    }
