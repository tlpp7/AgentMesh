# AdaptiveMesh v0.5 — feedback-guided revisions

```mermaid
flowchart TD
  A[Objective] --> P[Producer]
  P --> V[Rule checks]
  V --> D{All pass?}
  D -->|yes| O[Accepted]
  D -->|no| F[Violations + previous output + score]
  F --> R[Reviser]
  R --> V
  V -->|budget/stagnation exhausted| X[Rejected]
```

The reviser receives explicit failures and earlier output. It is a Python callback, not an LLM. The score is the **fraction of passing rules**, not a general quality metric. Invalid rule checks are conservatively marked failed. Revisions stop when acceptance, budget exhaustion or sustained non-improvement occurs.

```bash
python examples/adaptive_demo.py
python -m pytest tests/test_adaptive.py -q
```

Limitations: synchronous callbacks, no persistence, no external model, no automated semantic judge. Production use needs callback isolation, timeouts and tests of adversarial constraints.
