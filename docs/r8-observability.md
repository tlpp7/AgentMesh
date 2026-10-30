# R8 — Correlated local telemetry and diagnostics

R7 is already implemented; R8 is the first missing stage of the interface/visualization path.

## Shipped

- A bounded (200 records), in-process, lock-protected telemetry journal.
- A random `trace_id` and optional SQLite `run_id` correlated with each completed FastAPI execution.
- `GET /api/v2/telemetry?limit=30` protected by the existing bearer token.
- A React **Observabilité R8** panel showing execution counts, observed P95 and individual trace identifiers.
- Python API/privacy tests and a React source contract test.

The journal records no prompts, agent outputs or authorization headers. Telemetry is not persisted and resets when FastAPI restarts. P95 is calculated from the returned sample, not from all process history.

## Codespaces

```bash
cd /workspaces/AgentMesh
git pull --ff-only origin main
source .venv/bin/activate
python -m pip install -e '.[dev,api]' httpx
python -m pytest tests/test_r8_telemetry.py tests/test_r8_frontend.py -v
python -m pytest -q
# Start API in one terminal, optionally enable SQLite with AGENTMESH_DB_PATH:
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8001
```

In another terminal:

```bash
cd /workspaces/AgentMesh/apps/web-v2
npm install
npm run typecheck
npm run build
npm run dev
```

Run an execution, then click **Charger les métriques** in the R8 panel.

## Limitations / next steps

This is not OpenTelemetry distributed instrumentation: there are no propagated traceparent headers, subspans, exporters, collectors, cross-worker storage or cross-service timing estimates yet. For a real distributed tracing architecture, introduce an optional OTel SDK/instrumentation with explicit exporters and scrubbed attributes; do not expose telemetry publicly without auth and retention controls. R23 (interactive atlas), R25 (command center) and R26 (decision analytics) are future stages.
