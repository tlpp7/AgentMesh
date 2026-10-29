"""Explicit, opt-in integration contracts; no arbitrary remote HTTP or tool execution."""
from dataclasses import dataclass, asdict
from typing import Callable
from math import isfinite

@dataclass(frozen=True)
class AgentState:
    latency_ms: float
    error_rate: float
    cost_units: float
    quality_score: float
    def __post_init__(self):
        values=(self.latency_ms,self.error_rate,self.cost_units,self.quality_score)
        if not all(isfinite(v) for v in values) or self.latency_ms<0 or self.cost_units<0 or not 0<=self.error_rate<=1 or not 0<=self.quality_score<=1:
            raise ValueError("invalid typed agent state")
    def vector(self): return list(asdict(self).values())

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str = ""
    requires_approval: bool = True

class ControlledAdapter:
    """In-process wrapper for trusted callbacks; explicit named tools and approval."""
    def __init__(self, tools: dict[str,tuple[ToolSpec,Callable]], approve: Callable[[ToolSpec,dict],bool] | None=None):
        self.tools=dict(tools)
        self.approve=approve

    def invoke(self,name: str, arguments: dict) -> dict:
        if name not in self.tools: raise ValueError("tool not allowlisted")
        if not isinstance(arguments,dict): raise ValueError("arguments must be a dict")
        spec, callback=self.tools[name]
        if spec.requires_approval and (self.approve is None or not self.approve(spec,arguments)):
            return {"status":"denied","tool":name}
        result=callback(dict(arguments))
        return {"status":"ok","tool":name,"result":result}

def state_from_metrics(metrics: dict) -> AgentState:
    """Typed mapping only; never infer 'quality' from pass/fail automatically."""
    required=("latency_ms","error_rate","cost_units","quality_score")
    if not isinstance(metrics,dict) or any(key not in metrics for key in required):
        raise ValueError("explicitly provide all four state fields")
    return AgentState(*(float(metrics[k]) for k in required))
