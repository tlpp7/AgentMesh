"""Demonstrate explicit feedback-driven correction without external AI."""
import json
from agentmesh.adaptive import AdaptiveMesh, Rule

def producer(objective):
    return "Analysis: " + objective

def reviser(objective, feedback):
    text=feedback.previous_output
    if "requires_review" in feedback.violations:
        text += "\nReview: assumptions checked."
    if "requires_plan" in feedback.violations:
        text += "\nPlan: test, benchmark, compare."
    return text

rules=[Rule("requires_review",lambda x:"Review:" in x),
       Rule("requires_plan",lambda x:"Plan:" in x)]
result=AdaptiveMesh(producer,reviser,rules,max_attempts=4).run(
    "Design a constraint-aware orchestration engine")
print(json.dumps(result.to_dict(),indent=2))
