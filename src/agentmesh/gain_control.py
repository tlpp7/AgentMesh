"""Gain selection for bounded linear reflexive feedback."""
from dataclasses import dataclass
from math import isfinite
from .inverse import reflexive_feedback
from .micro import feedback_stability

@dataclass(frozen=True)
class GainChoice:
    gain: float
    residual: float
    iterations: int
    converged: bool
    certified: bool
    history: tuple

def compare_gains(matrix, initial, target, *, gains=(0.1,0.25,0.5,0.75,1.0), max_steps=100, tolerance=1e-7, bounds=None):
    if not gains or max_steps<1 or not isfinite(tolerance) or tolerance<=0:
        raise ValueError("invalid search configuration")
    options=[]
    for raw in gains:
        gain=float(raw)
        if not isfinite(gain) or gain<=0:
            raise ValueError("gains must be finite and positive")
        cert=feedback_stability(matrix,gain).sufficient_contraction
        result=reflexive_feedback(matrix,initial,target,gain=gain,max_steps=max_steps,tol=tolerance,bounds=bounds)
        options.append(GainChoice(gain,result.residual,result.iterations,result.converged,cert,result.history))
    # Prefer successful runs, then fastest success, then smallest residual.
    best=min(options,key=lambda o:(not o.converged,o.iterations if o.converged else max_steps,o.residual))
    return {"best":best,"candidates":options}
