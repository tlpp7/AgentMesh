# AgentMesh capability layers — customer-driven roadmap

This is a proposed roadmap, **not** a measured customer survey.

| Layer | User-facing outcome | Technical interface | Validation before shipping |
| --- | --- | --- | --- |
| 0. Request | Describe a task and desired result | Issue / UI schema | Complete acceptance criteria |
| 1. Repository | Authorized read and PR workflow | GitHub MCP | Least privilege; no direct-main edits |
| 2. Orchestration | Break task into verifiable steps | AsyncMesh + dependency DAG | Dependency/timeout tests |
| 3. Constraints | Reject unmet requirements | AdaptiveMesh + typed rules | Negative tests; false-positive review |
| 4. Numeric | Explore feedback/cross-coupling | inverse.py + hybrid.py | Residual and conditioning tests |
| 5. Automation | Trigger on GitHub events | n8n | Signed/authenticated event validation |
| 6. Browser QA | Execute visible UI checks | Automa | Deterministic selectors/evidence |
| 7. Observability | Trace attempts and failures | SQLite + event API | Privacy, retention and access testing |
| 8. Governance | Keep humans in control | PR approval gates | Audit trail, scoped permissions |
| 9. Adoption | Install, demo and contribute | README + examples + screenshots | Fresh onboarding tests |

Suggested MVP: a scoped GitHub issue triggers an n8n check that calls AgentMesh, produces a limited report and attaches it to a PR for **human approval**. No automatic merge.

The key metrics should be independently measured: successful CI checks, precision of constraint classification, end-to-end latency, reviewer time, false approvals and incident rate. Do not invent benchmark figures.
