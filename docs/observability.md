# Observability in AgentMesh 0.2

Metrics are run-local; duration values are informative rather than strict benchmarks.

```mermaid
flowchart LR
 A[Agent] --> T[Timed trace]
 T --> S[Supervisor]
 S --> R[RunResult]
 R --> J[JSONL file opt-in]
 J --> M[Aggregate report]
```

No network transmission. Use --trace-file to store runs. Note: traces include prompts and outputs; avoid secrets and do not commit local traces.
Agent exceptions are re-raised, not silently converted to successful runs.
