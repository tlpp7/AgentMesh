# R3 — Transactional event journal and replay

R3 adds an **opt-in SQLite event journal** while keeping the original RunStore and port 8000 dashboard unchanged. FastAPI (port 8001) persists deterministic `POST /api/v2/run` results only when `AGENTMESH_DB_PATH` is set.

## Start in Codespaces

Terminal A:

```bash
cd /workspaces/AgentMesh
source .venv/bin/activate
python -m pip install -e '.[dev,api]' httpx
export AGENTMESH_DB_PATH="$PWD/.local/agentmesh-r3.db"
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8001
```

Terminal B:

```bash
cd /workspaces/AgentMesh/apps/web-v2
npm install
npm run typecheck
npm run build
npm run dev
```

On React port 5173, run an objective, then click **Actualiser** under **Historique SQLite R3** and **Rejouer** on an entry. When the API token is enabled on FastAPI, enter the same token in the React interface. Keep forwarded ports private.

## New API routes

- `GET /api/v2/runs?limit=30`: recent runs.
- `GET /api/v2/runs/{id}`: run payload.
- `GET /api/v2/runs/{id}/events?after=0&limit=100`: ordered event replay.

The event cursor is an integer sequence; `after` is exclusive. Protected routes require the same bearer token as execution when enabled.

## Validation

```bash
python -m pytest tests/test_r3_journal.py tests/test_r3_frontend.py -v
python -m pytest -q
cd apps/web-v2 && npm run typecheck && npm run build
```

## Scope and limitations

This journal persists **completed deterministic runs and their trace events**, not live events emitted while the run is executing. Replay means reconstructing a historical trace for inspection, **not re-executing agents**. The in-memory EventBus still exists independently and is not yet integrated with Redis or a durable multi-worker pub/sub system. PostgreSQL migrations, a true live SSE/WebSocket streaming channel, cancellation, retention scheduling, and full failure recovery are pending.

Do not use this experimental API as a public internet-facing deployment without stronger authentication, HTTPS and operational safeguards.
