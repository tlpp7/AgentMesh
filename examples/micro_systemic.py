"""Demonstrate inverse microprograms with non-LLM numeric states."""
import json
from dataclasses import asdict
from agentmesh.micro import (
    cross_sensitivity, interval_feasibility, feedback_stability,
    reflexive_adaptation,
)

matrix=[[1.0,0.25],[0.2,1.0]]
result={
    "cross":cross_sensitivity(matrix,[0.2,-0.1],[1,1]),
    "feasibility":interval_feasibility(matrix,[0,0],[1,1],[1.5,0.4]),
    "stability":asdict(feedback_stability(matrix,0.4)),
    "adaptation":reflexive_adaptation(matrix,[0,0],[1,0.5],[0.1,0.2,0.4],steps=40),
}
print(json.dumps(result,indent=2))
