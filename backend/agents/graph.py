"""LangGraph orchestration: Needs -> Research -> Eligibility -> Planning -> Verification."""
from langgraph.graph import END, StateGraph

from backend.agents.eligibility import eligibility_agent
from backend.agents.needs import needs_agent
from backend.agents.planning import planning_agent
from backend.agents.research import research_agent
from backend.agents.state import GuideState
from backend.agents.verification import verification_agent

AGENTS = [
    ("needs", "Needs Assessment Agent", needs_agent),
    ("research", "Research Agent", research_agent),
    ("eligibility", "Eligibility Agent", eligibility_agent),
    ("planning", "Planning Agent", planning_agent),
    ("verification", "Verification Agent", verification_agent),
]


def build_graph():
    g = StateGraph(GuideState)
    for key, _, fn in AGENTS:
        g.add_node(key, fn)
    g.set_entry_point(AGENTS[0][0])
    for (a, _, _), (b, _, _) in zip(AGENTS, AGENTS[1:]):
        g.add_edge(a, b)
    g.add_edge(AGENTS[-1][0], END)
    return g.compile()


guide_graph = build_graph()
