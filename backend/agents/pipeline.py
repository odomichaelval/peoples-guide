import json
import re
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END

from backend.config import OLLAMA_URL, CHAT_MODEL
from backend.rag.retriever import search

llm = ChatOllama(model=CHAT_MODEL, base_url=OLLAMA_URL, temperature=0, format="json")

DISCLAIMER = (
    "This is general guidance based on public information, not legal or financial advice. "
    "Check eligibility with the service before applying."
)


def ask_json(system: str, user: str) -> dict:
    text = llm.invoke([("system", system), ("human", user)]).content
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        return json.loads(m.group(0)) if m else {}


class State(TypedDict, total=False):
    situation: str
    needs: list
    evidence: list
    options: list
    steps: list
    result: dict


def needs_agent(state: State) -> State:
    out = ask_json(
        "You help UK residents find public support. Read the person's situation and list "
        "their main needs as short phrases (e.g. 'help paying rent', 'emergency money', "
        "'council tax help', 'income while unemployed'). "
        'Reply as JSON: {"needs": ["..."]} with at most 4 items.',
        state["situation"],
    )
    return {"needs": out.get("needs", [])[:4] or ["general support"]}


def research_agent(state: State) -> State:
    seen, evidence = set(), []
    for need in state["needs"]:
        for hit in search(f"{need}. {state['situation'][:200]}", k=3):
            key = (hit["source"], hit["text"][:60])
            if key not in seen:
                seen.add(key)
                evidence.append(hit)
    return {"evidence": evidence[:8]}


def _numbered(evidence):
    return "\n\n".join(f"[{i}] ({e['source']}) {e['text']}" for i, e in enumerate(evidence))


def eligibility_agent(state: State) -> State:
    out = ask_json(
        "You assess which UK support options may apply. Use ONLY the numbered evidence. "
        "Never invent schemes, amounts or rules. If the evidence does not support an option, "
        "leave it out. Reply as JSON: "
        '{"options": [{"name": "...", "why_it_may_apply": "...", "evidence_ids": [0]}]}',
        f"Situation: {state['situation']}\n\nNeeds: {state['needs']}\n\nEvidence:\n{_numbered(state['evidence'])}",
    )
    return {"options": out.get("options", [])}


def planner_agent(state: State) -> State:
    out = ask_json(
        "Turn the support options into a short ordered action plan (3 to 6 steps) in plain "
        "English, most urgent first. Use ONLY the options and evidence given. Reply as JSON: "
        '{"steps": [{"action": "...", "evidence_ids": [0]}]}',
        f"Situation: {state['situation']}\n\nOptions: {json.dumps(state['options'])}\n\n"
        f"Evidence:\n{_numbered(state['evidence'])}",
    )
    return {"steps": out.get("steps", [])}


def verifier_agent(state: State) -> State:
    ev = state["evidence"]

    def sources(ids):
        valid = [i for i in ids if isinstance(i, int) and 0 <= i < len(ev)]
        return sorted({ev[i]["source"] for i in valid})

    options, steps = [], []
    for o in state["options"]:
        s = sources(o.get("evidence_ids", []))
        if s:
            options.append({"name": o.get("name"), "why": o.get("why_it_may_apply"), "sources": s})
    for st in state["steps"]:
        s = sources(st.get("evidence_ids", []))
        if s:
            steps.append({"action": st.get("action"), "sources": s})
    return {
        "result": {
            "needs": state["needs"],
            "options": options,
            "plan": steps,
            "dropped_unsupported": (len(state["options"]) - len(options))
            + (len(state["steps"]) - len(steps)),
            "disclaimer": DISCLAIMER,
        }
    }


def build_graph():
    g = StateGraph(State)
    g.add_node("needs", needs_agent)
    g.add_node("research", research_agent)
    g.add_node("eligibility", eligibility_agent)
    g.add_node("planner", planner_agent)
    g.add_node("verifier", verifier_agent)
    g.set_entry_point("needs")
    g.add_edge("needs", "research")
    g.add_edge("research", "eligibility")
    g.add_edge("eligibility", "planner")
    g.add_edge("planner", "verifier")
    g.add_edge("verifier", END)
    return g.compile()


_graph = build_graph()


def run_pipeline(situation: str) -> dict:
    return _graph.invoke({"situation": situation})["result"]