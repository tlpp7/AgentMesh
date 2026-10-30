# Repository-wide audit — R1/R9 environment regression (2026-10-30)

## Observed in user's Codespaces session

Python 3.14.2, pytest 9.2.0. `tests/test_r10_outbox.py`: **3 passed**. Full suite: **187 passed, 5 failed**, all from `tests/test_r1_api.py`. R1 requests returned HTTP 503 instead of 200/422.

## Confirmed root cause

`apps/api/main.py` has a new R9 dependency for POST /api/v2/run. With `AGENTMESH_R9_ENFORCE=1` and no configured token it emits `503 r9_requires_token`, before the R1 endpoint runs.

The original R1 fixture removed `AGENTMESH_API_TOKEN` but did not remove `AGENTMESH_R9_ENFORCE`. Shell environment inherited from a Codespaces session activated R9. The R1 fixture has been updated to explicitly remove both environment settings in its legacy compatibility scenarios. The explicit bearer test also disables R9 for isolation.

Run `python -m pytest tests/test_r1_api.py -q` followed by `python -m pytest -q` **with existing R9 environment still enabled** to verify isolation.

## Source inspection coverage

The repository tree contains 165 entries. Reviewed these areas and the relevant source contracts:
- Legacy server/core, optional FastAPI R1, R9 security policy and test fixture.
- Existing R3 journal and R10 SQLite outbox.
- R7 Playwright config and browser specs, R8 telemetry, R15 difference constraints.
- New R11 planning module, start/stop scripts, React API client and primary GitHub Actions workflow.
- Packaging and dependency declarations.

## Findings and priorities

| Priority | Area | Finding | Action |
| --- | --- | --- | --- |
| P0 resolved in code | R1/R9 tests | Inherited enforcement flag breaks R1 backward-compatibility tests | Test fixture isolates R9 flag; verify in Codespaces |
| P1 | R7 Playwright | `reuseExistingServer: !CI` can connect to an unrelated local server on 8001/5173, yielding misleading results | Set CI=1 for isolated E2E runs; add strict server identification |
| P1 | R10 Outbox | `r10_outbox` and R3 persistence are independent; run and event insertions aren't atomic across both stores | Integrate transactional writes and dispatcher, add crash tests |
| P1 | R11 Planner | Planner module exists but is not yet wired to runtime nor accompanied by dedicated tests in the repository | Add unit, cancellation, priority and dependency tests before adoption |
| P1 | Secrets and auth | R9 supports a single operator bearer token, not multi-user RBAC; counters are process-local | Implement principal identity and centralized quotas before public access |
| P2 | Frontend reproducibility | Root tree currently contains `package.json` but no committed `apps/web-v2/package-lock.json`; CI uses `npm install` | Commit lockfile and transition to `npm ci` |
| P2 | R8 telemetry | Metrics are in-process and reset on restart; no distributed tracing | Add optional trace propagation and exporters |
| P2 | Runtime supervision | Launch helper uses PID files and local health checks; it is not a production process manager | Use systemd/container or orchestrator with restarts and termination policy |
| P2 | Dependency warnings | User observed Starlette's deprecation warning for `httpx` TestClient | Track dependency compatibility separately, without blind upgrades |
| P2 | R15 solver | Floating-point graph feasibility is not a formal numeric proof | Add boundary/property tests and optional exact rational backend |

## Suggested validation

```bash
cd /workspaces/AgentMesh
git pull --ff-only origin main
source .venv/bin/activate
env | grep -E '^AGENTMESH_(R9_ENFORCE|API_TOKEN)=' | sed -E 's/(API_TOKEN=).*/\1[REDACTED]/'
python -m pytest tests/test_r1_api.py tests/test_r9_security.py tests/test_r10_outbox.py -v
python -m pytest -q
cd apps/web-v2
npm install
npm run typecheck && npm run build
CI=1 npm run test:e2e
```

**Audit limits**: these findings come from reviewing the repository tree and selected implementation files, plus the user-provided test log. The complete repository has **not** been executed in this analysis environment; do not treat untested components as certified. No production security audit or proof of end-to-end success is implied.
