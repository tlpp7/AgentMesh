# R1 — Additive FastAPI adapter

**Scope:** A separately deployed FastAPI service that calls the original Python Mesh. The legacy `server.py` and `web/` remain unchanged.

## Run locally

```bash
python -m pip install -e '.[dev,api]'
python -m pytest tests/test_r1_api.py -v
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8001
```

Visit `http://127.0.0.1:8001/docs`, `GET /api/health` and `POST /api/v2/run`.

### Request JSON

```json
{"objective":"Build a pipeline","attempts":3,"contains":"pipeline"}
```

The API has strict `RunRequest` input validation. It calls the existing `Mesh`, retains legacy output fields and adds `observability`. If `AGENTMESH_API_TOKEN` is configured, a bearer token is mandatory for the run route. Health and OpenAPI docs are public; do **not** directly expose this experimental adapter to the internet.

## Compatibility boundaries

- R1 currently covers the deterministic `agents` route only, **not** all legacy `/api/run` modes such as numerical inversion, LLM, gain search, or hybrid.
- FastAPI validation returns HTTP 422; the legacy server commonly returns 400. That difference is intentional and documented.
- The new service does not serve the original dashboard, provide multi-user accounts, enforce rate limits, or implement persistent storage.
- CI skips the optional API tests when extras are not installed. Run `pip install -e '.[dev,api]'` and then run the tests to validate R1.
- Do not put API tokens in source control or exposed URLs.

## R1 acceptance gates

1. Core and optional tests pass.
2. Matching test payloads produce equal deterministic `accepted`, `output`, `attempts`, and `violations`.
3. OpenAPI, strict request bounds, and bearer authorization tests pass.
4. The old dashboard remains working on port 8000 independently.
5. Other legacy API modes are migrated individually with parity tests, not silently replaced.
