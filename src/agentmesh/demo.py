"""Offline example agents; no LLM connection."""
from .core import Agent, Task

def analyze(text: str, task: Task) -> str:
    return f"Analysis: {text.strip()}"

def propose(text: str, task: Task) -> str:
    return f"{text}\nProposal: define inputs, invariants, outputs, and tests."

def critique(text: str, task: Task) -> str:
    return f"{text}\nReview: verify assumptions and bound failure modes."

def default_agents() -> list[Agent]:
    return [
        Agent("analyzer", analyze),
        Agent("proposer", propose),
        Agent("critic", critique),
    ]
