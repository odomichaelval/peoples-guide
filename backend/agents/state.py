import operator
from typing import Annotated, Any, TypedDict


class GuideState(TypedDict, total=False):
    query: str                      # resident's own words
    location: str                   # e.g. "Sheffield"
    needs: dict[str, Any]           # Needs Assessment output
    evidence: list[dict]            # Research output (retrieved chunks)
    eligibility: list[dict]         # Eligibility output
    plan: dict[str, Any]            # Planning output
    verification: dict[str, Any]    # Verification output
    trace: Annotated[list[dict], operator.add]  # agent activity log for the UI
