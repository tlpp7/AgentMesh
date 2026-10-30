# R9 — Security baseline for multi-agent execution

R7 is already implemented; the next unimplemented phase in the Intelligence multi-agent path was R9.

## New controls

- `security_policy.py`: explicit viewer/operator/supervisor permissions, per-agent read-only tool capabilities, and a thread-safe in-memory sliding-window limiter.
- FastAPI execution endpoint `POST /api/v2/run`: opt-in gate using `AGENTMESH_R9_ENFORCE=1`; requires `AGENTMESH_API_TOKEN` and uses the configured token as a single **operator** principal.
- Default behavior preserves legacy R1–R7 flows; the original `server.py` is not modified.

## Codespaces

```bash
cd /workspaces/AgentMesh
git pull --ff-only origin main
source .venv/bin/activate
python -m pip install -e '.[dev,api]' httpx
python -m pytest tests/test_r9_security.py -v
python -m pytest -q
export AGENTMESH_API_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export AGENTMESH_R9_ENFORCE=1
export AGENTMESH_R9_RATE_LIMIT=30
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8001
```

This is an **initial security layer, not a full identity provider**. The bearer token corresponds to one operator identity, not multiple independent users. Role/capability rules are defined and tested but not yet wired into every tool/MCP invocation. The limiter is in-process and not shared across workers; use a distributed atomic rate store for production. No rate limiting is applied to the legacy port 8000.

Do not expose FastAPI publicly without HTTPS, reverse-proxy protections, real user identities, centralized quotas, audit trails, and deployment hardening.

Next path: R11 dynamic orchestration → R12 extended MCP → R14 structured memory. All require separate implementation and validation.
