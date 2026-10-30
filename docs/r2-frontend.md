# R2 — Additive React frontend connected to FastAPI

The original dashboard and server.py remain unchanged (port 8000).
The V2 frontend is independently served by Vite (port 5173) and proxies /api requests to FastAPI on 127.0.0.1:8001 during local development.

## Start the API (terminal 1)

```bash
cd /workspaces/AgentMesh
source .venv/bin/activate
python -m pip install -e '.[dev,api]' httpx
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8001
```

## Start the frontend (terminal 2)

```bash
cd /workspaces/AgentMesh/apps/web-v2
npm install
npm run typecheck
npm run build
npm run dev
```

Open the forwarded port 5173 in Codespaces (keep private). The frontend can run deterministic agents, view the resulting graph, filter traces and export the result as JSON. The API token field stores credentials in page memory only. If AGENTMESH_API_TOKEN is set on the FastAPI process, enter the same token in the frontend.

## Verification

```bash
cd /workspaces/AgentMesh
python -m pytest tests/test_r2_frontend.py tests/test_r1_api.py -q
python -m pytest -q
cd apps/web-v2
npm run typecheck
npm run build
npm audit
```

## Limits

- The Vite /api proxy is development-only. Production deployments must configure a same-origin reverse proxy and TLS.
- The graph renders post-run events; it is not live streaming.
- The FastAPI adapter currently supports deterministic agent runs, not the full legacy feature set.
- No browser end-to-end tests or deployed authentication provider yet.
- The Pydantic contract returns validation errors with HTTP 422. Keep the original dashboard running independently until API parity is established.
