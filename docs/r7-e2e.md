# R7 — End-to-end reliability testing

The legacy `server.py`, `web/` and original orchestration engines are unchanged. R7 adds **opt-in Playwright browser tests**, FastAPI/SQLite restart-compatibility tests and a reproducible local test harness.

## Validation in Codespaces

```bash
cd /workspaces/AgentMesh
git pull --ff-only origin main
source .venv/bin/activate
python -m pip install -e '.[dev,api]' httpx
python -m pytest tests/test_r7_restart.py -v
cd apps/web-v2
npm install
npx playwright install --with-deps chromium
npm run typecheck
npm run build
npm run test:e2e
```

Playwright starts FastAPI (port 8001), Vite (port 5173), and uses a local-only test token and a temporary SQLite path. **Stop other processes bound to these ports** or set `CI=1` to avoid test-server reuse. Keep Codespaces forwarded ports private.

### Coverage
- React -> FastAPI -> Mesh -> SQLite -> history -> replay
- Wrong bearer token -> HTTP 401 displayed by UI
- Stored run survives recreation of the FastAPI application instance (not yet a simulated process crash)
- Protected history routes reject unauthorized requests

### Limitations

This does not yet test a real OS-process restart, concurrent failures, database corruption, live SSE, or a hardened production reverse proxy. The database filename in Playwright config is reserved for isolated tests; don't use it for real user data.

Run `npm audit` after installing Playwright; commit the updated `package-lock.json` so CI and Codespaces get identical dependencies. R7 is only fully validated after the browser suite runs successfully.
