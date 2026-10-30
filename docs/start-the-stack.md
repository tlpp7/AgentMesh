# Start AgentMesh (Codespaces, opt-in V2 stack)

This helper launches only the optional **FastAPI 8001 + React/Vite 5173** stack, preserving legacy `server.py` on 8000.

```bash
cd /workspaces/AgentMesh
git pull --ff-only origin main
source .venv/bin/activate
python -m pip install -e '.[dev,api]' httpx
cd apps/web-v2 && npm install && npm run build && cd ../..
python scripts/start_stack.py
cat .local/stack/token
```

Visit your Codespaces forwarded **5173** page (set the port to **Private**) and enter the token in **Token API (uniquement en mémoire)**. Click Exécuter, Actualiser history, and Charger les métriques. The Vite `/api` proxy connects to local FastAPI 8001. No public exposure or tunnel is configured automatically.

The manager enables R9 for POST /api/v2/run and persists completed runs under `.local/agentmesh.db`. Token is generated automatically unless `AGENTMESH_API_TOKEN` is already set. It is stored in `.local/stack/token` with owner-only file permissions. The user should not share it.

```bash
python scripts/stop_stack.py
tail -n 40 .local/stack/api.log
tail -n 40 .local/stack/web.log
```

If ports 8001 or 5173 are already occupied, stop the old services before starting the manager. This script is intended for local Codespaces prototyping, not for production supervision or automatic restart.
