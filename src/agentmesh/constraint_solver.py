"""R15: bounded difference-constraints feasibility with an explainable infeasible core.

Supports x <= u, x >= l, x - y <= c. Finite floats only.
Not a general SAT, SMT or nonlinear optimization solver.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Bound:
    name: str
    variable: str
    kind: str
    value: float
    other: str = ""

    def __post_init__(self):
        if not isinstance(self.name,str) or not self.name.strip() or len(self.name)>100:
            raise ValueError("invalid constraint name")
        if not isinstance(self.variable,str) or not self.variable.isidentifier() or self.variable=="__zero__":
            raise ValueError("invalid variable")
        if self.kind not in ("upper","lower","difference"):
            raise ValueError("unsupported kind")
        if type(self.value) not in (int,float) or not isfinite(self.value):
            raise ValueError("finite numeric value required")
        if self.kind=="difference" and (not isinstance(self.other,str) or not self.other.isidentifier() or self.other=="__zero__"):
            raise ValueError("difference requires other variable")
        if self.kind!="difference" and self.other:
            raise ValueError("other only valid for difference")

def _solve(constraints):
    names={"__zero__"}
    for c in constraints:
        names.add(c.variable)
        if c.kind=="difference":names.add(c.other)
    nodes=sorted(names)
    edges=[]
    for c in constraints:
        if c.kind=="upper":edges.append(("__zero__",c.variable,c.value))
        elif c.kind=="lower":edges.append((c.variable,"__zero__",-c.value))
        else:edges.append((c.other,c.variable,c.value))
    dist={name:0.0 for name in nodes}
    for _ in range(len(nodes)):
        changed=False
        for origin,destination,weight in edges:
            candidate=dist[origin]+weight
            if candidate<dist[destination]:
                dist[destination]=candidate
                changed=True
        if not changed:break
    else:
        return None
    offset=dist["__zero__"]
    return {name:value-offset for name,value in dist.items() if name!="__zero__"}

def solve_constraints(constraints,explain=True):
    """Return a witness if feasible; an irreducible core otherwise.

    The core is deletion-minimal, not necessarily minimum-cardinality.
    """
    constraints=list(constraints)
    if len(constraints)>64:raise ValueError("maximum 64 constraints")
    if any(not isinstance(c,Bound) for c in constraints):
        raise TypeError("expected Bound constraints")
    if len({c.name for c in constraints})!=len(constraints):
        raise ValueError("constraint names must be unique")
    variables={c.variable for c in constraints}
    variables.update(c.other for c in constraints if c.other)
    if len(variables)>32:raise ValueError("maximum 32 variables")
    witness=_solve(constraints)
    if witness is not None:
        return {"feasible":True,"witness":witness,"unsat_core":[],"solver":"difference_constraints"}
    core=list(constraints)
    if explain:
        index=0
        while index<len(core):
            candidate=core[:index]+core[index+1:]
            if _solve(candidate) is None:core=candidate
            else:index+=1
    return {"feasible":False,"witness":None,"unsat_core":[c.name for c in core],
            "solver":"difference_constraints"}
