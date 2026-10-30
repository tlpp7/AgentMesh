# AgentMesh modular extension plan (additive, not a rewrite)

All original entry points remain: `server.py`, `web/`, `src/agentmesh/core.py`, the async DAG, inverse models and old CLI.

## Modules delivered

| Module | Location | Status |
| --- | --- | --- |
| Extension registry | `src/agentmesh/extensions.py` | In-process, opt-in |
| Typed events | `src/agentmesh/events.py` | In-memory queue, not distributed |
| Evaluation counters | `src/agentmesh/evaluations.py` | Outcome counts, not semantic evaluation |
| Optional FastAPI | `apps/api/main.py` | Separate API, routes not yet parity-tested |
| React / TypeScript + React Flow | `apps/web-v2/` | Experimental interface scaffold |
| PostgreSQL adapter | `src/agentmesh/postgres_adapter.py` | Connection factory only, no migrations |
| OpenTelemetry adapter | `src/agentmesh/telemetry_adapter.py` | Explicit spans; no exporter configured |
| OpenAI / GitHub | `src/agentmesh/model_gateway.py`, `github_workflow.py` | Existing optional integrations |
| MCP | `mcp` optional dependency group | Transport implementation pending |
| Rust/Zig | Not installed | Only consider after proven hotspots |
| Redis / Temporal | Not installed | Deferred until a concrete durability need |

## Keep using the original application

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python server.py --host 127.0.0.1 --port 8000
```

## Try optional FastAPI independently

```bash
python -m pip install -e '.[api]'
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8001
```

It exposes `GET /api/health` and `POST /api/v2/run`. This is a separate service, not a replacement for the historical API.

## Try the React scaffold

```bash
cd apps/web-v2
npm install
npm run build
npm run dev
```

This is a *static demonstration* of the network view; no backend data is wired yet. Node/npm installation and successful browser rendering require verification in Codespaces.

## Architectural safeguards

- Avoid launching two APIs on the same port.
- Install optional extras only for modules you need.
- Keep model credentials in protected environment variables.
- Do not expose experimental servers publicly.
- Do not call the PostgreSQL connector a migration until tables, transactions, backup and integration tests exist.
- Do not call the event queue durable; it has no replay or persistence.
- Do not claim Rust or Zig speedups until the Python baseline is measured.
