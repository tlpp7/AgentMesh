# Architecture

AgentMesh runs a fixed series of local agents and validates their final text against user-defined predicates.

```mermaid
flowchart LR
  T[Task] --> M[Mesh]
  M --> A[Analyzer]
  A --> B[Proposer]
  B --> C[Critic]
  C --> V[Constraints]
  V -->|pass| O[Result + Trace]
  V -->|fail, retries left| M
  V -->|fail, exhausted| R[Rejected + Trace]
```

## Guarantees
- Bounded number of attempts.
- Explicit accept/reject status and violations.
- Deterministic offline demo.
- No arbitrary tool execution or network access.

## Current limitations
- Sequential execution only.
- Constraints inspect the final textual output.
- No sandbox for third-party agents: use only trusted Python callables.
- No LLM adapters, distributed execution, or persistent storage yet.
