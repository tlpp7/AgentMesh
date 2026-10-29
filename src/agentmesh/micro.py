"""Systemic inverse microprograms for small finite-dimensional real systems."""
from dataclasses import dataclass
from math import sqrt, isfinite

def _matrix(a):
    a = [list(map(float, row)) for row in a]
    if not a or not a[0] or any(len(row) != len(a[0]) for row in a):
        raise ValueError("matrix must be rectangular and nonempty")
    if not all(isfinite(v) for row in a for v in row):
        raise ValueError("non-finite matrix")
    return a

def _mv(a, x):
    return [sum(v*z for v,z in zip(row,x)) for row in a]

def _norm(x):
    return sqrt(sum(z*z for z in x))

def cross_sensitivity(matrix, perturbation, baseline=None):
    """Exact linear effects Δy=AΔx and off-diagonal contributions."""
    a = _matrix(matrix)
    dx = list(map(float, perturbation))
    if len(dx) != len(a[0]) or not all(map(isfinite, dx)):
        raise ValueError("perturbation dimension mismatch")
    effects = _mv(a, dx)
    result = {"effects": effects, "magnitude": _norm(effects),
              "cross_only": [sum(a[i][j]*dx[j] for j in range(len(dx)) if j != i)
                             for i in range(len(a))]}
    if baseline is not None:
        b = list(map(float, baseline))
        if len(b) != len(dx) or not all(map(isfinite, b)):
            raise ValueError("baseline dimension mismatch")
        result["before"] = _mv(a,b)
        result["after"] = _mv(a,[v+d for v,d in zip(b,dx)])
    return result

def interval_feasibility(matrix, lower, upper, target, atol=1e-9):
    """Prove exclusion of a target outside box-propagated coordinate intervals.
    Membership in all intervals does NOT establish joint feasibility.
    """
    a = _matrix(matrix)
    lo,hi,y = [list(map(float,v)) for v in (lower,upper,target)]
    if len(lo)!=len(a[0]) or len(hi)!=len(lo) or len(y)!=len(a):
        raise ValueError("dimension mismatch")
    if not all(isfinite(v) for v in lo+hi+y) or any(l>h for l,h in zip(lo,hi)):
        raise ValueError("invalid bounds")
    if not isfinite(atol) or atol<0:
        raise ValueError("invalid tolerance")
    envelopes = [(sum(c*(l if c>=0 else h) for c,l,h in zip(row,lo,hi)),
                  sum(c*(h if c>=0 else l) for c,l,h in zip(row,lo,hi)))
                 for row in a]
    violations = [i for i,((l,h),v) in enumerate(zip(envelopes,y))
                  if v<l-atol or v>h+atol]
    return {"envelopes": envelopes,"outside_coordinates": violations,
            "status": "proven_infeasible" if violations else "undetermined"}

@dataclass(frozen=True)
class SpectralEstimate:
    norm_upper_bound: float
    sufficient_contraction: bool
    spectral_radius_lower_bound: float

def feedback_stability(coupling, gain):
    """||I-gain*W||∞<1 suffices for global contraction without clipping."""
    a = _matrix(coupling)
    n=len(a)
    if any(len(row)!=n for row in a) or not isfinite(gain) or gain<=0:
        raise ValueError("square matrix and positive gain required")
    t=[[float(i==j)-gain*a[i][j] for j in range(n)] for i in range(n)]
    upper=max(sum(abs(v) for v in row) for row in t)
    return SpectralEstimate(upper, upper<1.0, 0.0)

def reflexive_adaptation(coupling, state, target, gains, steps=30, bounds=None):
    """Evaluate finite candidate gains; return best observed final residual."""
    from .inverse import reflexive_feedback
    if not gains or steps<1:
        raise ValueError("gains and steps required")
    candidates=[]
    for gain in gains:
        result=reflexive_feedback(coupling,state,target,gain=gain,max_steps=steps,bounds=bounds)
        candidates.append({"gain":gain,"state":list(result.state),
                           "residual":result.residual,"converged":result.converged,
                           "iterations":result.iterations})
    return {"best":min(candidates,key=lambda c:c["residual"]), "candidates":candidates}
