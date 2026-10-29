"""Hybrid supervisor: explicit text revision and bounded numeric inverse control."""
from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Callable
from .adaptive import AdaptiveMesh, Rule
from .inverse import inverse_linear, reflexive_feedback, matvec
from .micro import cross_sensitivity, feedback_stability, interval_feasibility

@dataclass(frozen=True)
class HybridResult:
    mode: str
    accepted: bool
    output: dict
    diagnostics: dict
    def to_dict(self):
        return {"mode": self.mode, "accepted": self.accepted,
                "output": self.output, "diagnostics": self.diagnostics}

def run_text(objective: str, requirements: list[str], max_attempts=4) -> HybridResult:
    if not isinstance(objective, str) or not objective.strip():
        raise ValueError("nonempty objective required")
    if not isinstance(requirements,list) or len(requirements)>20 or any(not isinstance(x,str) or not x or len(x)>120 for x in requirements):
        raise ValueError("invalid requirements")
    if len(set(requirements)) != len(requirements):
        raise ValueError("requirements must be unique")
    def produce(goal):
        return "Analysis: " + goal
    def revise(goal, feedback):
        result=feedback.previous_output
        for failure in feedback.violations:
            idx=int(failure.split(":")[1])
            result += "\n" + requirements[idx] + " completed locally."
        return result
    rules=[Rule(f"required:{i}",lambda text,term=term:term in text) for i,term in enumerate(requirements)]
    result=AdaptiveMesh(produce,revise,rules,max_attempts=max_attempts).run(objective)
    return HybridResult("text",result.accepted,result.to_dict(),
                        {"fraction_passing":result.metrics["final_score"],
                         "violations":result.violations})

def run_numeric(matrix, target, *, gain=0.5, max_steps=100,
                lower=None, upper=None, ridge=0.001) -> HybridResult:
    """Analyze control; accept only convergence AND no violated supplied bounds.

    Interval analysis is a necessary exclusion test, never a feasibility proof.
    """
    a=[list(map(float,row)) for row in matrix]
    y=list(map(float,target))
    if not a or not a[0] or len(a)>10 or len(a[0])>10:
        raise ValueError("invalid matrix shape")
    n=len(a[0])
    if len(a)!=n or len(y)!=n or any(len(row)!=n for row in a):
        raise ValueError("reflexive control needs a square matrix and matching target")
    if not all(isfinite(v) for row in a for v in row) or not all(map(isfinite,y)):
        raise ValueError("nonfinite data")
    if max_steps<1 or max_steps>1000:
        raise ValueError("max_steps outside 1..1000")
    if (lower is None)!=(upper is None):
        raise ValueError("lower and upper must be supplied together")
    bounds=None
    envelope=None
    if lower is not None:
        lo=list(map(float,lower));hi=list(map(float,upper))
        if len(lo)!=n or len(hi)!=n or any(not isfinite(l) or not isfinite(h) or l>h for l,h in zip(lo,hi)):
            raise ValueError("invalid state bounds")
        bounds=list(zip(lo,hi))
        envelope=interval_feasibility(a,lo,hi,y)
    candidate=inverse_linear(a,y,ridge=ridge)
    initial=[0.0]*n
    if bounds is not None:
        initial=[max(lo,min(hi,0.0)) for lo,hi in bounds]
    result=reflexive_feedback(a,initial,y,gain=gain,max_steps=max_steps,bounds=bounds)
    prediction=matvec(a,list(result.state))
    residual=sqrt(sum((v-t)**2 for v,t in zip(prediction,y)))
    stability=feedback_stability(a,gain)
    accepted=result.converged and residual<=1e-7 and (envelope is None or envelope["status"]!="proven_infeasible")
    output={"inverse_regularized":candidate,"state":list(result.state),
            "predicted_output":prediction,"target":y,"residual":residual,
            "iterations":result.iterations,"history":list(result.history)}
    diagnostics={"converged":result.converged,
                 "contraction_sufficient":stability.sufficient_contraction,
                 "norm_upper_bound":stability.norm_upper_bound,
                 "feasibility":envelope["status"] if envelope else "not_checked",
                 "intervals":envelope,
                 "sensitivity":cross_sensitivity(a,[0.1]*n)}
    return HybridResult("numeric",accepted,output,diagnostics)

def run_hybrid(*,objective=None,requirements=None,matrix=None,target=None,**kwargs):
    """Dispatch explicitly; no automatic conversion from strings to numeric states."""
    if matrix is not None or target is not None:
        if matrix is None or target is None:
            raise ValueError("matrix and target required together")
        return run_numeric(matrix,target,**kwargs)
    if objective is None:
        raise ValueError("objective or numeric system required")
    return run_text(objective,requirements or [],max_attempts=kwargs.get("max_attempts",4))
