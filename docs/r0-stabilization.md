# R0 — Stabilization and migration readiness

R0 preserves the legacy server, dashboard, orchestration engines and APIs. It establishes reproducible environmental checks and a compatibility gate before migrating to the optional V2 modules.

## Verified baseline supplied by Codespaces
- 134 pytest cases passed on Python 3.14.2 (before R0 additions).
- Legacy API port 8000 and FastAPI port 8001 are separate services.
- React V2 build succeeded; npm reported one moderate-severity vulnerability requiring investigation.
- The old 401 failures were caused by exported server authentication during isolated test requests and have been corrected by tests/conftest.py.

## Commands for validation

```bash
cd /workspaces/AgentMesh
git pull --ff-only origin main
source .venv/bin/activate
python -m pip install -e '.[dev]'
python scripts/r0_doctor.py --strict --output r0-environment.json
python -m compileall -q src apps server.py scripts
python -m pytest tests/test_r0_stabilization.py -v
python -m pytest -q
cd apps/web-v2
npm audit
npm run build
```

R0 doctor records Python version, availability of **optional** packages and existence of compatibility-critical source files. It never exports keys, runs model calls or changes configuration. Optional packages missing are not a failure of the legacy core. The CI matrix now includes Python 3.14.

## Exit conditions
1. Whole pytest suite green in Codespaces and GitHub CI.
2. Legacy dashboard and `/api/run` checked manually with the API token.
3. FastAPI `/api/v2/run` smoke tested independently.
4. React V2 build and npm security report reviewed.
5. p50/p95 benchmark baseline stored and measured on a consistent runner.
6. No secrets in diagnostic reports or uploaded artifacts.

R0 has added its guards, but exit conditions 1–5 require new execution evidence after this commit. Do not claim production-readiness solely from unit tests.
