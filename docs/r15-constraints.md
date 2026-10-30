# R15 — Explainable bounded difference constraints

R15 begins the Constraints and Research track after the already implemented R7. It is **additive**: legacy text constraints, Mesh, FastAPI, React and SQLite remain unchanged.

## Model

A finite set of scalar variables may be constrained by:
- `lower`: x >= L
- `upper`: x <= U
- `difference`: x - y <= c

The solver transforms each inequality into a weighted directed graph. Bellman–Ford relaxation finds a feasible potential (witness), while a negative-weight cycle implies infeasibility. An optional deletion procedure identifies a **deletion-minimal unsatisfiable subset**, not necessarily the smallest core.

## Codespaces

```bash
cd /workspaces/AgentMesh
git pull --ff-only origin main
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest tests/test_r15_constraint_solver.py -v
python -m pytest -q
python scripts/r15_demo.py
```

## Python contract

```python
from agentmesh.constraint_solver import Bound, solve_constraints
rules=[Bound("minimum","x","lower",3),Bound("maximum","x","upper",2)]
print(solve_constraints(rules))
# {'feasible': False, 'witness': None, 'unsat_core': ['minimum', 'maximum'], ...}
```

## Constraints and limitations

This is not a general-purpose SAT/SMT, nonlinear solver, linear-programming solver or certified floating-point proof system. Numbers are finite Python floats with ordinary floating-point comparison, so rounding and near-boundary cases must not be treated as rigorous proofs. Limits: at most 64 constraints and 32 variables, suitable for controlled experiments; the explanation step can run the feasibility algorithm repeatedly. No dynamic dispatch from arbitrary LLM text to this solver and no external side effects.

Next planned modules: R16 inverse parameter inference, R17 inter-model coupling, R18 decision control, R19 simulation. They are not implemented by R15.
