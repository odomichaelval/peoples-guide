"""Agent 4 - Planning: builds a prioritised, practical action plan."""
import json
import time

from backend import llm
from backend.agents.state import GuideState

SYSTEM = """You are the Planning Agent for People's Guide.
Create a short, prioritised action plan the resident can follow this week.
Put urgent needs (no money for food, eviction, crisis) first. Use plain English (reading age ~11).
Only use services and URLs from the eligibility list provided. Each step must cite refs.

Return ONLY JSON:
{
  "headline": "one encouraging sentence summarising the plan",
  "steps": [
    {"priority": 1, "title": "short action", "service": "service name",
     "why": "why this helps them", "how": "concrete how-to (apply online, call, documents)",
     "timeframe": "today | this week | this month", "url": "official url", "refs": ["S1"]}
  ],
  "documents_to_gather": ["ID, tenancy agreement, bank statements, ..."],
  "questions_to_answer": ["facts the resident should check that affect eligibility"]
}
Give 3 to 7 steps."""

CRISIS_STEP = {
    "priority": 0,
    "title": "Get urgent help now if you are in danger or have nowhere to stay tonight",
    "service": "Emergency and crisis support",
    "why": "Your safety comes first.",
    "how": "Call 999 in an emergency. Samaritans are free 24/7 on 116 123. "
           "For homelessness tonight, contact Sheffield City Council's housing service or Shelter's helpline.",
    "timeframe": "today",
    "url": "https://england.shelter.org.uk/get_help",
    "refs": [],
    "verified": True,
    "verification_note": "Standard crisis guidance",
}


async def planning_agent(state: GuideState) -> GuideState:
    t = time.time()
    services = [s for s in state.get("eligibility", []) if s.get("likelihood") != "unlikely"]
    if not services:
        plan = {
            "headline": "We couldn't match specific services yet - Citizens Advice can review your situation with you.",
            "steps": [{
                "priority": 1, "title": "Talk to Citizens Advice", "service": "Citizens Advice",
                "why": "Free, confidential advice on benefits, debt and housing.",
                "how": "Use the website to find your local office or call their adviceline.",
                "timeframe": "this week", "url": "https://www.citizensadvice.org.uk/", "refs": [],
            }],
            "documents_to_gather": [], "questions_to_answer": [],
        }
    else:
        user = (
            f"Resident needs:\n{json.dumps(state['needs'], indent=1)}\n\n"
            f"Eligible / possible services:\n{json.dumps(services, indent=1)}"
        )
        plan = await llm.chat_json(SYSTEM, user)
        plan.setdefault("steps", [])
    if state.get("needs", {}).get("safety_flags"):
        plan["steps"].insert(0, dict(CRISIS_STEP))
    plan["steps"].sort(key=lambda s: s.get("priority", 99))
    return {
        "plan": plan,
        "trace": [{
            "agent": "planning",
            "message": f"Built an action plan with {len(plan['steps'])} steps",
            "seconds": round(time.time() - t, 1),
        }],
    }
