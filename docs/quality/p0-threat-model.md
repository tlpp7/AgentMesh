# Q06 — Threat model and security acceptance (draft)
Scope: React/Vite browser, FastAPI, SQLite, local subprocesses, MCP tools, Codespaces, CI.
Trust boundaries: browser -> proxy -> API; API -> persistence; trusted agent -> tool callback; GitHub Actions -> release artifact.

| Threat | Attack / failure | Primary control | Evidence required |
|---|---|---|---|
| Authentication bypass | Missing/forged bearer | Fail closed when R9 enabled | 401/503 tests |
| Cross-run access | Guess another run UUID | Ownership/identity checks | Multi-principal tests (NOT IMPLEMENTED) |
| Resource exhaustion | Abusive runs | Rate/budget gates | 429 and load tests |
| Tool escalation | Agent invoking unlisted tool | Default-deny permission scopes | Negative tests |
| Prompt/tool injection | Untrusted content requests actions | Never treat text as authorization | Human approval, tool policy tests |
| Secrets exfiltration | Token leaked in logs/frontend storage | Mask and keep transient | Secret scans |
| Persistence disruption | Power loss, duplicated events | Outbox idempotency; backup/restore | Crash recovery tests (INCOMPLETE) |
| Supply-chain compromise | Untrusted dependency/action | Locked versions, signed provenance | SBOM/SLSA evidence (P1) |

OWASP ASVS 5.0 and OWASP API Top 10 are control catalogs, not certifications. This threat register is a starting point, not evidence of full coverage. Do not expose the application publicly until authorization, TLS/proxy, tool sandboxing and security review are completed.
