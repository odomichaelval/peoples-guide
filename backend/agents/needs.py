"""Agent 1 - Needs Assessment: turns a resident's story into structured needs."""
import time

from backend import llm
from backend.agents.state import GuideState

SYSTEM = """You are the Needs Assessment Agent for People's Guide, a UK public services navigator.
Read the resident's situation and extract their circumstances and support needs.
Be kind and non-judgemental. Do not invent facts the resident did not say.

Return ONLY JSON with this shape:
{
  "summary": "one or two sentences restating the situation",
  "circumstances": {
    "location": "town/city or null",
    "employment": "employed | unemployed | recently_unemployed | self_employed | student | retired | unknown",
    "housing": "renting_private | renting_social | homeowner | living_with_family | homeless | at_risk_of_homelessness | unknown",
    "household": "who lives with them, if stated, else unknown",
    "age_group": "under_25 | 25_to_state_pension_age | pension_age | unknown",
    "has_children": true/false/null,
    "disability_or_health_condition": true/false/null,
    "caring_responsibilities": true/false/null,
    "income_notes": "any income/savings/benefits mentioned, else unknown"
  },
  "needs": [
    {"category": "income | housing | council_tax | employment | food | energy | health | mental_health | education | childcare | debt | legal | other",
     "description": "what they need help with", "urgency": "immediate | soon | planning"}
  ],
  "safety_flags": ["only if there is risk of harm, abuse, homelessness tonight, or crisis; else empty"],
  "missing_information": ["facts that would change eligibility, e.g. savings, partner's income"],
  "search_queries": ["4-8 short search queries to find relevant UK/Sheffield support services"]
}"""


async def needs_agent(state: GuideState) -> GuideState:
    t = time.time()
    user = f"Resident location (if known): {state.get('location') or 'Sheffield'}\n\nResident says:\n\"\"\"{state['query']}\"\"\""
    needs = await llm.chat_json(SYSTEM, user)
    needs.setdefault("needs", [])
    needs.setdefault("search_queries", [state["query"]])
    needs.setdefault("safety_flags", [])
    return {
        "needs": needs,
        "trace": [{
            "agent": "needs",
            "message": f"Identified {len(needs['needs'])} support need(s): "
                       + ", ".join(n.get("category", "?") for n in needs["needs"]),
            "seconds": round(time.time() - t, 1),
        }],
    }
